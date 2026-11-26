import importlib.util
import shutil
import subprocess
import sys

def _probe(name):
    path = shutil.which(name)
    if not path: return {"status": "UNAVAILABLE", "path": None, "version": None}
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
        version = (r.stdout or r.stderr).splitlines()[0]
    except Exception:
        version = "Detected; version probe failed"
    return {"status": "AVAILABLE", "path": path, "version": version}

def detect_capabilities():
    modules = {m: ("AVAILABLE" if importlib.util.find_spec(m) else "UNAVAILABLE")
        for m in ("PIL", "numpy", "cv2", "jsonschema", "pytest", "moviepy", "av")}
    return {"python": {"status": "AVAILABLE", "version": sys.version.split()[0]},
        "ffmpeg": _probe("ffmpeg"), "ffprobe": _probe("ffprobe"),
        "node": _probe("node"), "chromium": _probe("chromium"), "espeak": _probe("espeak"),
        "python_modules": modules, "image_generation": "NOT_TESTED_BY_LOCAL_ENGINE",
        "video_generation": "NOT_TESTED_BY_LOCAL_ENGINE",
        "semantic_music_detection": "UNAVAILABLE", "visual_policy_certification": "UNAVAILABLE"}
