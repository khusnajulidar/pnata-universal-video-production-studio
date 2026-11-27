"""Strict v0.3 project and policy validation. No rendering is performed here."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .timeline_v3 import TimelineV3Error, validate_timeline

_SCHEMA_PATH=Path(__file__).resolve().parents[1]/"schema"/"scene-project-v0.3.schema.json"
class SceneV3Error(ValueError):
    """Invalid or unsafe v0.3 project."""

def validate_scene_project(path):
    project_path=Path(path).resolve()
    if not project_path.is_file(): raise SceneV3Error(f"Project not found: {project_path}")
    try: project=json.loads(project_path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise SceneV3Error(f"Cannot read project JSON: {exc}") from exc
    schema=json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors=sorted(Draft202012Validator(schema).iter_errors(project),key=lambda e:list(map(str,e.absolute_path)))
    if errors:
        e=errors[0]; loc=".".join(map(str,e.absolute_path)) or "<root>"
        raise SceneV3Error(f"Schema error at {loc}: {e.message}")
    root=project_path.parent; assets={}
    for a in project["assets"]:
        aid=a["id"]
        if aid in assets: raise SceneV3Error(f"Duplicate asset id: {aid}")
        assets[aid]=a
        candidate=(root/a["path"]).resolve()
        try: candidate.relative_to(root)
        except ValueError as exc: raise SceneV3Error(f"Asset path escapes project directory: {a['path']}") from exc
        if not candidate.is_file(): raise SceneV3Error(f"Asset file not found for {aid}: {candidate}")
        if a["rights_status"]!="cleared" or a["policy_reviewed"] is not True: raise SceneV3Error(f"Asset {aid} has not passed rights and policy review.")
        if a["media_type"] in {"image","video"} and a.get("contains_embedded_audio",False): raise SceneV3Error(f"Embedded audio is forbidden in visual asset {aid}.")
    total=0.0; scene_ids=set()
    for s in project["scenes"]:
        if s["id"] in scene_ids: raise SceneV3Error(f"Duplicate scene id: {s['id']}")
        scene_ids.add(s["id"]); duration=float(s["duration"]); total+=duration
        if s.get("transition_in",{}).get("type")=="dissolve":
            td=float(s["transition_in"].get("duration",0))
            if td<=0 or td>duration: raise SceneV3Error(f"Invalid dissolve duration in scene {s['id']}.")
        layer_ids=set()
        for layer in s["layers"]:
            lid=layer["id"]
            if lid in layer_ids: raise SceneV3Error(f"Duplicate layer id {lid} in scene {s['id']}.")
            layer_ids.add(lid); start,end=float(layer["start"]),float(layer["end"])
            if end<=start or end>duration: raise SceneV3Error(f"Invalid layer time range for {lid} in scene {s['id']}.")
            if layer["type"]=="image":
                a=assets.get(layer["asset_id"])
                if not a or a["media_type"]!="image": raise SceneV3Error(f"Image layer {lid} references an unknown/non-image asset.")
            for fid in [layer.get("font_asset_id"),*layer.get("font_fallback_asset_ids",[])]:
                if fid and (fid not in assets or assets[fid]["media_type"]!="font"): raise SceneV3Error(f"Layer {lid} references an unknown/non-font asset.")
            for prop,points in layer.get("keyframes",{}).items():
                if prop not in {"x","y","scale","opacity","rotation"}: raise SceneV3Error(f"Unsupported keyframe property {prop!r} in layer {lid}.")
                times=[float(p["time"]) for p in points]
                if times!=sorted(times) or len(times)!=len(set(times)): raise SceneV3Error(f"Keyframe times must be strictly increasing in layer {lid}.")
                if any(t>end-start for t in times): raise SceneV3Error(f"Keyframe exceeds layer duration in layer {lid}.")
            if layer.get("overflow")=="shrink_to_fit":
                minimum=layer.get("min_font_size")
                if minimum is None or minimum>layer.get("font_size",minimum): raise SceneV3Error(f"Layer {lid} shrink_to_fit needs a valid min_font_size.")
    if total+1e-6<float(project["duration"]): raise SceneV3Error("Scene durations do not cover project duration.")
    track_ids=set()
    for t in project.get("audio_tracks",[]):
        if t["id"] in track_ids: raise SceneV3Error(f"Duplicate audio track id: {t['id']}")
        track_ids.add(t["id"]); a=assets.get(t["asset_id"])
        if not a or a["media_type"]!="audio": raise SceneV3Error(f"Audio track {t['id']} references an unknown/non-audio asset.")
        if a.get("audio_category")!=t["category"]: raise SceneV3Error(f"Audio category mismatch for track {t['id']}.")
        if t.get("reviewed_non_musical") is not True: raise SceneV3Error(f"Audio track {t['id']} lacks non-musical human review.")
        if t.get("loop",False): raise SceneV3Error(f"Audio looping is not supported in v0.3: {t['id']}.")
        if t["start"]+t["duration"]>project["duration"]+1e-6: raise SceneV3Error(f"Audio track {t['id']} exceeds project duration.")
        if t.get("fade_in",0)+t.get("fade_out",0)>t["duration"]: raise SceneV3Error(f"Audio fades exceed track duration for {t['id']}.")
    try: validate_timeline(project)
    except TimelineV3Error as exc: raise SceneV3Error(str(exc)) from exc
    return project,root
