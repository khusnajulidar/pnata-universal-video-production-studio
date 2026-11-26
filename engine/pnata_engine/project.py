import json
from pathlib import Path

class ProjectError(ValueError):
    pass

def load_project(path):
    file_path = Path(path).resolve()
    if not file_path.is_file():
        raise ProjectError(f"Project not found: {file_path}")
    data = json.loads(file_path.read_text(encoding="utf-8"))
    required = ("title", "width", "height", "fps", "policy", "scenes")
    missing = [key for key in required if key not in data]
    if missing:
        raise ProjectError(f"Missing keys: {', '.join(missing)}")
    if not isinstance(data["scenes"], list) or not data["scenes"]:
        raise ProjectError("At least one scene is required.")
    if data["width"] < 16 or data["height"] < 16 or data["fps"] <= 0:
        raise ProjectError("Invalid dimensions or frame rate.")
    for i, scene in enumerate(data["scenes"]):
        if float(scene.get("duration", 0)) <= 0:
            raise ProjectError(f"Scene {i} needs positive duration.")
    return data, file_path.parent
