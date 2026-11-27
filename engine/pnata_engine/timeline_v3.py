"""Deterministic scene timing, visibility windows, and caption validation."""
from dataclasses import dataclass


class TimelineV3Error(ValueError):
    """Invalid timeline, caption cue, or safe-margin configuration."""


@dataclass(frozen=True)
class SceneWindow:
    scene_id: str
    start: float
    end: float


def scene_windows(project):
    """Return sequential scene windows in project time; transitions do not alter duration."""
    cursor = 0.0
    result = []
    for scene in project.get("scenes", []):
        duration = float(scene["duration"])
        if duration <= 0:
            raise TimelineV3Error(f"Scene {scene.get('id')} must have positive duration.")
        result.append(SceneWindow(scene["id"], cursor, cursor + duration))
        cursor += duration
    if cursor + 1e-6 < float(project["duration"]):
        raise TimelineV3Error("Scene sequence does not cover project duration.")
    return tuple(result)


def seconds_to_frame(seconds, fps):
    """Quantize seconds to the nearest frame index using deterministic half-up rounding."""
    if fps <= 0 or seconds < 0:
        raise TimelineV3Error("seconds must be non-negative and fps must be positive.")
    return int(float(seconds) * int(fps) + 0.5)


def frame_to_seconds(frame, fps):
    if frame < 0 or fps <= 0:
        raise TimelineV3Error("frame must be non-negative and fps must be positive.")
    return int(frame) / int(fps)


def active_layers_at(project, time_seconds):
    """Return visible layers at a global time; visibility intervals are [start, end)."""
    t = float(time_seconds)
    if t < 0 or t >= float(project["duration"]):
        return ()
    active = []
    for window, scene in zip(scene_windows(project), project["scenes"]):
        if window.start <= t < window.end:
            local = t - window.start
            for layer in scene.get("layers", []):
                if float(layer["start"]) <= local < float(layer["end"]):
                    active.append({"scene_id": scene["id"], "layer": layer,
                                   "local_time": local, "global_start": window.start + float(layer["start"]),
                                   "global_end": window.start + float(layer["end"])})
    return tuple(active)


def caption_cues(project):
    """Return caption cues mapped from scene-local to global project time."""
    result = []
    for window, scene in zip(scene_windows(project), project["scenes"]):
        for cue in scene.get("captions", []):
            item = dict(cue)
            item["scene_id"] = scene["id"]
            item["global_start"] = window.start + float(cue["start"])
            item["global_end"] = window.start + float(cue["end"])
            result.append(item)
    return tuple(result)


def validate_timeline(project):
    """Validate cue IDs/timing and keep caption boxes inside normalized safe margins."""
    windows = scene_windows(project)
    margins = {"left": 0.05, "right": 0.05, "top": 0.05, "bottom": 0.05}
    margins.update(project.get("safe_margins", {}))
    if margins["left"] + margins["right"] >= 1 or margins["top"] + margins["bottom"] >= 1:
        raise TimelineV3Error("Opposing safe margins must leave a positive content area.")
    for window, scene in zip(windows, project["scenes"]):
        ids = set()
        for cue in scene.get("captions", []):
            cid = cue["id"]
            if cid in ids:
                raise TimelineV3Error(f"Duplicate caption id {cid} in scene {scene['id']}.")
            ids.add(cid)
            start, end = float(cue["start"]), float(cue["end"])
            if end <= start or end > float(scene["duration"]):
                raise TimelineV3Error(f"Invalid caption time range for {cid} in scene {scene['id']}.")
            x, y = float(cue["x"]), float(cue["y"])
            right, bottom = x + float(cue["width"]), y + float(cue["height"])
            if x < margins["left"] or y < margins["top"] or right > 1 - margins["right"] or bottom > 1 - margins["bottom"]:
                raise TimelineV3Error(f"Caption {cid} exceeds the configured safe margins.")
    return True
