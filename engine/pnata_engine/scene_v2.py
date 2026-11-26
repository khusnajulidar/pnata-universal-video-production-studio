"""Engine-neutral v0.2 scene model and deterministic keyframe evaluation.

Supported values are numeric properties only. Visual-policy compliance remains a
human review gate; this module does not certify that geometry or images are safe.
"""
import json
from pathlib import Path

class SceneV2Error(ValueError):
    pass

EASINGS = {"linear", "ease_in", "ease_out", "ease_in_out"}

def _ease(t, name):
    if name == "linear": return t
    if name == "ease_in": return t * t
    if name == "ease_out": return 1 - (1 - t) * (1 - t)
    if name == "ease_in_out":
        return 2 * t * t if t < .5 else 1 - ((-2 * t + 2) ** 2) / 2
    raise SceneV2Error(f"Unsupported easing: {name}")

def evaluate_keyframes(keyframes, time_value, default):
    """Evaluate ordered numeric keyframes at seconds; clamp outside the range."""
    if not keyframes:
        return float(default)
    points = sorted(keyframes, key=lambda p: float(p["time"]))
    if any(float(p["time"]) < 0 for p in points):
        raise SceneV2Error("Keyframe time cannot be negative.")
    if any(p.get("ease", "linear") not in EASINGS for p in points):
        raise SceneV2Error("Unsupported keyframe easing.")
    if time_value <= float(points[0]["time"]):
        return float(points[0]["value"])
    if time_value >= float(points[-1]["time"]):
        return float(points[-1]["value"])
    for left, right in zip(points, points[1:]):
        t0, t1 = float(left["time"]), float(right["time"])
        if t0 <= time_value <= t1:
            if t1 <= t0:
                raise SceneV2Error("Keyframe times must be strictly increasing.")
            amount = _ease((time_value - t0) / (t1 - t0), left.get("ease", "linear"))
            return float(left["value"]) + (float(right["value"]) - float(left["value"])) * amount
    return float(default)

def load_scene_project(path):
    p = Path(path).resolve()
    if not p.is_file():
        raise SceneV2Error(f"Project not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    for key in ("title", "width", "height", "fps", "duration", "scenes", "policy"):
        if key not in data: raise SceneV2Error(f"Missing project field: {key}")
    if int(data["width"]) < 16 or int(data["height"]) < 16:
        raise SceneV2Error("Canvas dimensions must be at least 16x16.")
    if not (1 <= int(data["fps"]) <= 120):
        raise SceneV2Error("FPS must be between 1 and 120.")
    if float(data["duration"]) <= 0 or not data["scenes"]:
        raise SceneV2Error("Project duration and scene list must be positive/non-empty.")
    if data["policy"].get("music") != "forbidden" or data["policy"].get("complete_living_beings") != "forbidden":
        raise SceneV2Error("P'Nata hard policy flags are mandatory.")
    total = 0.0
    root = p.parent
    for si, scene in enumerate(data["scenes"]):
        duration = float(scene.get("duration", 0))
        if duration <= 0: raise SceneV2Error(f"Scene {si} needs positive duration.")
        total += duration
        if scene.get("transition_in", {}).get("type", "cut") not in {"cut", "dissolve"}:
            raise SceneV2Error(f"Scene {si} has unsupported transition.")
        if scene.get("transition_in", {}).get("type") == "dissolve":
            td = float(scene["transition_in"].get("duration", 0))
            if td < 0 or td > duration: raise SceneV2Error("Invalid dissolve duration.")
        if scene.get("visual_reviewed_policy_compliant") is not True:
            raise SceneV2Error(f"Scene {si} requires human visual-policy review.")
        for li, layer in enumerate(scene.get("layers", [])):
            kind = layer.get("type")
            if kind not in {"text", "rect", "ellipse", "line", "image"}:
                raise SceneV2Error(f"Scene {si} layer {li}: unsupported type {kind!r}.")
            if kind == "image":
                asset = Path(layer.get("path", ""))
                asset = asset if asset.is_absolute() else root / asset
                if not asset.is_file(): raise SceneV2Error(f"Image asset not found: {asset}")
                if layer.get("asset_reviewed_policy_compliant") is not True:
                    raise SceneV2Error(f"Image asset requires visual-policy review: {asset}")
            for prop, frames in layer.get("keyframes", {}).items():
                if prop not in {"x", "y", "scale", "opacity", "rotation"}:
                    raise SceneV2Error(f"Unsupported animated property: {prop}")
                previous = -1
                for point in sorted(frames, key=lambda x: float(x["time"])):
                    current = float(point["time"])
                    if current <= previous: raise SceneV2Error("Keyframe times must be strictly increasing.")
                    if current > duration: raise SceneV2Error("Keyframe exceeds scene duration.")
                    previous = current
                    if point.get("ease", "linear") not in EASINGS: raise SceneV2Error("Unsupported easing.")
    if total + 1e-6 < float(data["duration"]):
        raise SceneV2Error("Scene durations do not cover project duration.")
    return data, root
