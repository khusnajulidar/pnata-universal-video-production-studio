import json
import shutil
import subprocess
from pathlib import Path

class QCError(RuntimeError):
    pass

def probe_video(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe: raise QCError("FFprobe unavailable.")
    p = Path(path)
    if not p.is_file() or p.stat().st_size == 0: raise QCError("Output missing or empty.")
    result = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    if not videos: raise QCError("No video stream found.")
    return {"file": str(p), "size_bytes": p.stat().st_size,
        "duration": float(data.get("format", {}).get("duration", 0)),
        "video": videos[0], "audio_streams": [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]}

def write_qc_report(video_path, report_path):
    report = probe_video(video_path)
    report["checks"] = {"file_nonempty": True, "video_stream_present": True,
        "duration_positive": report["duration"] > 0,
        "audio_content_semantically_reviewed": False,
        "visual_policy_reviewed_by_human": False}
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
