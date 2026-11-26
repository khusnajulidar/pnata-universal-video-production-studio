from pathlib import Path

ALLOWED_AUDIO_ROLES = {"voiceover", "speech", "sfx", "ambience"}
FORBIDDEN_AUDIO_ROLES = {"music", "soundtrack", "instrumental", "song", "beat", "melody"}

class PolicyError(ValueError):
    pass

def validate_audio_track(track):
    role = str(track.get("role", "")).strip().lower()
    if role in FORBIDDEN_AUDIO_ROLES or role not in ALLOWED_AUDIO_ROLES:
        raise PolicyError(f"Audio role {role!r} is forbidden or unsupported.")
    if track.get("human_reviewed_non_musical") is not True:
        raise PolicyError("Audio requires human_reviewed_non_musical=true.")
    if not Path(track.get("path", "")).is_file():
        raise PolicyError(f"Audio asset does not exist: {track.get('path')}")

def validate_project_policy(project, root):
    policy = project.get("policy", {})
    if policy.get("music") != "forbidden":
        raise PolicyError("Project must set policy.music='forbidden'.")
    if policy.get("complete_living_beings") != "forbidden":
        raise PolicyError("Project must forbid complete depictions of living beings.")
    for track in project.get("audio", []):
        item = dict(track)
        p = Path(item.get("path", ""))
        item["path"] = str(p if p.is_absolute() else root / p)
        validate_audio_track(item)
    for scene in project.get("scenes", []):
        if scene.get("image"):
            p = Path(scene["image"])
            p = p if p.is_absolute() else root / p
            if not p.is_file():
                raise PolicyError(f"Scene image not found: {p}")
            if scene.get("visual_reviewed_policy_compliant") is not True:
                raise PolicyError(f"Scene image requires human visual-policy review: {p}")
