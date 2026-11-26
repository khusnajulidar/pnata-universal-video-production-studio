"""Pillow/FFmpeg v0.2 raster backend: animated layers + cut/dissolve transitions.

This is a deterministic 2D compositor, not a substitute for a nonlinear editor,
3D renderer, footage editor, or semantic policy classifier.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .scene_v2 import load_scene_project, evaluate_keyframes

def _font(size, preferred=None):
    for candidate in (preferred, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=max(1, int(size)))
    return ImageFont.load_default()

def _value(layer, prop, local_t, default):
    return evaluate_keyframes(layer.get("keyframes", {}).get(prop, []), local_t, layer.get(prop, default))

def _draw_layer(canvas, layer, local_t, root, font_path):
    w, h = canvas.size
    x = _value(layer, "x", local_t, layer.get("x", .5)) * w
    y = _value(layer, "y", local_t, layer.get("y", .5)) * h
    scale = max(0.001, _value(layer, "scale", local_t, 1))
    opacity = max(0.0, min(1.0, _value(layer, "opacity", local_t, 1)))
    rotation = _value(layer, "rotation", local_t, 0)
    kind = layer["type"]
    if kind == "image":
        p = Path(layer["path"]); p = p if p.is_absolute() else root / p
        source = Image.open(p).convert("RGBA")
        box_w = int(layer.get("width", source.width) * scale)
        box_h = int(layer.get("height", source.height) * scale)
        source.thumbnail((max(1, box_w), max(1, box_h)), Image.Resampling.LANCZOS)
        layer_img = Image.new("RGBA", source.size, (0,0,0,0))
        layer_img.alpha_composite(source)
    else:
        box_w = int(float(layer.get("width", .5)) * w * scale)
        box_h = int(float(layer.get("height", .1)) * h * scale)
        layer_img = Image.new("RGBA", (max(1,box_w), max(1,box_h)), (0,0,0,0))
        d = ImageDraw.Draw(layer_img)
        color = layer.get("color", "#FFFFFF")
        if kind == "text":
            f = _font(int(layer.get("font_size", 48) * scale), font_path)
            text = str(layer.get("text", ""))
            anchor = "mm"
            d.text((box_w/2, box_h/2), text, font=f, fill=color, anchor=anchor,
                   stroke_width=int(layer.get("stroke_width", 0)),
                   stroke_fill=layer.get("stroke_color", "#000000"))
        elif kind == "rect":
            d.rounded_rectangle((0,0,box_w-1,box_h-1), radius=int(layer.get("radius", 0)*scale),
                                 fill=color, outline=layer.get("outline"), width=int(layer.get("outline_width", 1)))
        elif kind == "ellipse":
            d.ellipse((0,0,box_w-1,box_h-1), fill=color, outline=layer.get("outline"),
                      width=int(layer.get("outline_width", 1)))
        elif kind == "line":
            d.line((0,box_h/2,box_w,box_h/2), fill=color, width=max(1,int(layer.get("line_width", 4)*scale)))
    if rotation:
        layer_img = layer_img.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)
    alpha = layer_img.getchannel("A").point(lambda a: int(a * opacity))
    layer_img.putalpha(alpha)
    canvas.alpha_composite(layer_img, (int(x-layer_img.width/2), int(y-layer_img.height/2)))

def render_scene_project(project_path, output_path):
    project, root = load_scene_project(project_path)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg: raise RuntimeError("FFmpeg unavailable.")
    out = Path(output_path).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
    width, height, fps = int(project["width"]), int(project["height"]), int(project["fps"])
    with tempfile.TemporaryDirectory(prefix="pnata_v02_") as td:
        tmp = Path(td); frames_dir = tmp / "frames"; frames_dir.mkdir()
        previous = None; frame_index = 0
        for scene_index, scene in enumerate(project["scenes"]):
            duration = float(scene["duration"])
            count = max(1, round(duration * fps))
            transition = scene.get("transition_in", {"type":"cut"})
            dissolve_frames = round(float(transition.get("duration", 0))*fps) if transition.get("type") == "dissolve" else 0
            for local_frame in range(count):
                t = local_frame / fps
                canvas = Image.new("RGBA", (width,height), scene.get("background", "#101820"))
                for layer in scene.get("layers", []):
                    _draw_layer(canvas, layer, t, root, project.get("font"))
                if previous is not None and local_frame < dissolve_frames:
                    mix = (local_frame + 1) / max(1,dissolve_frames)
                    canvas = Image.blend(previous, canvas, mix)
                rgb = canvas.convert("RGB")
                frame_path = frames_dir / f"frame_{frame_index:08d}.png"
                rgb.save(frame_path, optimize=False)
                frame_index += 1
                if local_frame == count-1: previous = canvas
        pattern = str(frames_dir / "frame_%08d.png")
        subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-y","-framerate",str(fps),
            "-i",pattern,"-frames:v",str(frame_index),"-c:v","libx264","-preset",
            str(project.get("preset","medium")),"-crf",str(project.get("crf",20)),
            "-pix_fmt","yuv420p","-movflags","+faststart",str(out)],check=True)
    return out
