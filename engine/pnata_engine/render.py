import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .project import load_project
from .policy import validate_project_policy

def _font(size, preferred=None):
    for path in (preferred, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if path and Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()

def _wrap(draw, text, font, width):
    lines, current = [], ""
    for word in str(text).split():
        trial = (current + " " + word).strip()
        if current and draw.textbbox((0, 0), trial, font=font)[2] > width:
            lines.append(current); current = word
        else:
            current = trial
    if current: lines.append(current)
    return lines

def render_project(project_path, output_path):
    project, root = load_project(project_path)
    validate_project_policy(project, root)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg unavailable.")
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    width, height, fps = int(project["width"]), int(project["height"]), int(project["fps"])
    total_duration = sum(float(s["duration"]) for s in project["scenes"])
    with tempfile.TemporaryDirectory(prefix="pnata_") as td:
        temp = Path(td); concat = temp / "scenes.txt"; entries = []
        for i, scene in enumerate(project["scenes"], 1):
            if scene.get("image"):
                p = Path(scene["image"]); p = p if p.is_absolute() else root / p
                canvas = Image.open(p).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
            else:
                canvas = Image.new("RGB", (width, height), scene.get("background", "#101820"))
            draw = ImageDraw.Draw(canvas); margin = int(width * .09)
            y = int(height * float(scene.get("text_y", .35)))
            title_size = int(scene.get("title_size", max(24, width // 18)))
            body_size = int(scene.get("text_size", max(18, width // 30)))
            for key, size, color, gap in (
                ("title", title_size, scene.get("title_color", "#FFFFFF"), 1.25),
                ("text", body_size, scene.get("text_color", "#E8EDF2"), 1.5)):
                value = scene.get(key, "")
                if value:
                    font = _font(size, project.get("font"))
                    for line in _wrap(draw, value, font, width - 2 * margin):
                        draw.text((margin, y), line, font=font, fill=color,
                                  stroke_width=1 if key == "title" else 0,
                                  stroke_fill="#000000")
                        y += int(size * gap)
                    if key == "title": y += int(size * .5)
            frame = temp / f"scene_{i:04d}.png"; canvas.save(frame)
            entries.append((frame, float(scene["duration"])))
        with concat.open("w", encoding="utf-8") as f:
            for frame, duration in entries:
                f.write(f"file '{frame}'\nduration {duration:.6f}\n")
            f.write(f"file '{entries[-1][0]}'\n")
        silent = temp / "silent.mp4"
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-vf", f"fps={fps},format=yuv420p", "-c:v", "libx264",
            "-preset", "medium", "-crf", str(project.get("crf", 20)),
            "-movflags", "+faststart", str(silent)], check=True)
        tracks = project.get("audio", [])
        if not tracks:
            shutil.copy2(silent, out)
        else:
            cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent)]
            filters, labels = [], []
            for idx, track in enumerate(tracks, 1):
                p = Path(track["path"]); p = p if p.is_absolute() else root / p
                cmd += ["-i", str(p)]
                delay = max(0, int(float(track.get("start", 0)) * 1000))
                label = f"a{idx}"; labels.append(f"[{label}]")
                filters.append(f"[{idx}:a]adelay={delay}|{delay},volume={float(track.get('volume', 1.0))}[{label}]")
            filters.append("".join(labels) +
                f"amix=inputs={len(labels)}:duration=longest:normalize=0,apad=whole_dur={total_duration:.6f}[aout]")
            cmd += ["-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total_duration:.6f}",
                    "-movflags", "+faststart", str(out)]
            subprocess.run(cmd, check=True)
    return out
