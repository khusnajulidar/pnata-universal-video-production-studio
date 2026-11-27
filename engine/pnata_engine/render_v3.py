"""Integrated v0.3 Pillow/FFmpeg renderer for approved 2D scenes and timed captions."""
import json, math, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from .scene_v3 import validate_scene_project
from .timeline_v3 import scene_windows
from .layout_v3 import layout_text, draw_text_layout, fit_image
from .scene_v2 import evaluate_keyframes

class RenderV3Error(RuntimeError): pass

def _font_paths(project, root):
    return [str((root/a["path"]).resolve()) for a in project["assets"] if a["media_type"]=="font"]

def _animated(layer, prop, local_time, default):
    return evaluate_keyframes(layer.get("keyframes",{}).get(prop,[]),local_time,layer.get(prop,default))

def _place(canvas, layer_image, x, y, opacity=1, rotation=0):
    if rotation:
        layer_image=layer_image.rotate(-rotation,resample=Image.Resampling.BICUBIC,expand=True)
    if opacity<1:
        layer_image.putalpha(layer_image.getchannel("A").point(lambda a:int(a*max(0,min(1,opacity)))))
    canvas.alpha_composite(layer_image,(round(x-layer_image.width/2),round(y-layer_image.height/2)))

def _render_layer(canvas, layer, local_time, root, assets, font_paths):
    w,h=canvas.size
    t=max(0,local_time-float(layer["start"]))
    x=_animated(layer,"x",t,layer.get("x",.5))*w
    y=_animated(layer,"y",t,layer.get("y",.5))*h
    scale=max(.001,_animated(layer,"scale",t,layer.get("scale",1)))
    opacity=max(0,min(1,_animated(layer,"opacity",t,layer.get("opacity",1))))
    rotation=_animated(layer,"rotation",t,layer.get("rotation",0))
    kind=layer["type"]
    bw=max(1,round(float(layer.get("width",.5))*w*scale))
    bh=max(1,round(float(layer.get("height",.1))*h*scale))
    if kind=="image":
        asset=assets[layer["asset_id"]]; source=(root/asset["path"]).resolve()
        image=fit_image(source,(bw,bh),layer.get("fit","contain"),(layer.get("crop_anchor_x",.5),layer.get("crop_anchor_y",.5)))
    else:
        image=Image.new("RGBA",(bw,bh),(0,0,0,0)); d=ImageDraw.Draw(image); color=layer.get("color","#FFFFFF")
        if kind=="rect":
            d.rounded_rectangle((0,0,bw-1,bh-1),radius=round(float(layer.get("radius",0))*scale),fill=color,outline=layer.get("outline"),width=max(1,round(float(layer.get("outline_width",1))*scale)))
        elif kind=="ellipse":
            d.ellipse((0,0,bw-1,bh-1),fill=color,outline=layer.get("outline"),width=max(1,round(float(layer.get("outline_width",1))*scale)))
        elif kind=="line":
            d.line((0,bh//2,bw-1,bh//2),fill=color,width=max(1,round(float(layer.get("line_width",4))*scale)))
        elif kind=="text":
            font_ids=[layer["font_asset_id"]] if layer.get("font_asset_id") else []
            font_ids+=layer.get("font_fallback_asset_ids",[])
            paths=[str((root/assets[i]["path"]).resolve()) for i in font_ids]+font_paths
            layout=layout_text(layer["text"],(0,0,bw,bh),max(1,round(float(layer["font_size"])*scale)),paths,
                layer.get("horizontal_align","center"),layer.get("vertical_align","middle"),
                layer.get("line_spacing",1.2),round(float(layer.get("padding",0))*scale),
                layer.get("overflow","error"),round(float(layer["min_font_size"])*scale) if layer.get("min_font_size") else None)
            draw_text_layout(image,layer["text"],layout,layer.get("color","#FFFFFF"),round(float(layer.get("stroke_width",0))*scale),layer.get("stroke_color","#000000"))
    _place(canvas,image,x,y,opacity,rotation)

def _render_captions(canvas, scene, local_time, font_paths):
    w,h=canvas.size
    for cue in scene.get("captions",[]):
        if not (float(cue["start"])<=local_time<float(cue["end"])): continue
        box=(round(cue["x"]*w),round(cue["y"]*h),round(cue["width"]*w),round(cue["height"]*h))
        layout=layout_text(cue["text"],box,max(1,round(cue["font_size"])),font_paths,
            cue.get("horizontal_align","center"),"middle",1.15,0,"error")
        draw_text_layout(canvas,cue["text"],layout,cue.get("color","#FFFFFF"))

def render_video_v3(project_path, output_path, ffmpeg=None):
    project,root=validate_scene_project(project_path)
    binary=ffmpeg or shutil.which("ffmpeg")
    if not binary: raise RenderV3Error("FFmpeg unavailable.")
    out=Path(output_path).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    width,height,fps=int(project["width"]),int(project["height"]),int(project["fps"])
    windows=scene_windows(project); assets={a["id"]:a for a in project["assets"]}; fonts=_font_paths(project,root)
    target_frames=max(1,round(float(project["duration"])*fps))
    with tempfile.TemporaryDirectory(prefix="pnata_v03_") as td:
        frames=Path(td)/"frames"; frames.mkdir(); previous=None; transition_reference=None; active_scene_id=None
        for frame in range(target_frames):
            now=frame/fps
            pair=next(((win,scene) for win,scene in zip(windows,project["scenes"]) if win.start<=now<win.end),None)
            if pair is None: raise RenderV3Error(f"Timeline does not cover frame at {now:.4f}s.")
            win,scene=pair; local=now-win.start
            if scene["id"] != active_scene_id:
                transition_reference=previous.copy() if previous is not None else None
                active_scene_id=scene["id"]
            canvas=Image.new("RGBA",(width,height),scene.get("background",project.get("background","#101820")))
            for layer in scene.get("layers",[]):
                if float(layer["start"])<=local<float(layer["end"]):
                    _render_layer(canvas,layer,local,root,assets,fonts)
            _render_captions(canvas,scene,local,fonts)
            transition=scene.get("transition_in",{"type":"cut"})
            if transition_reference is not None and transition.get("type")=="dissolve":
                count=max(1,round(float(transition.get("duration",0))*fps))
                scene_frame=frame-round(win.start*fps)
                if scene_frame<count:
                    canvas=Image.blend(transition_reference,canvas,min(1,(scene_frame+1)/count))
            previous=canvas.copy()
            canvas.convert("RGB").save(frames/f"frame_{frame:08d}.png")
        cmd=[binary,"-hide_banner","-loglevel","error","-y","-framerate",str(fps),"-i",str(frames/"frame_%08d.png"),
             "-frames:v",str(target_frames),"-an","-c:v","libx264","-preset",str(project.get("preset","medium")),
             "-crf",str(project.get("crf",20)),"-pix_fmt","yuv420p","-movflags","+faststart",str(out)]
        try: subprocess.run(cmd,check=True,capture_output=True,text=True)
        except (OSError,subprocess.CalledProcessError) as exc: raise RenderV3Error(f"FFmpeg video render failed: {exc}") from exc
    return out

def mux_audio_v3(video_path,audio_path,output_path,ffmpeg=None):
    binary=ffmpeg or shutil.which("ffmpeg")
    if not binary: raise RenderV3Error("FFmpeg unavailable.")
    out=Path(output_path).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    cmd=[binary,"-hide_banner","-loglevel","error","-y","-i",str(video_path),"-i",str(audio_path),
         "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(out)]
    try: subprocess.run(cmd,check=True,capture_output=True,text=True)
    except (OSError,subprocess.CalledProcessError) as exc: raise RenderV3Error(f"FFmpeg audio mux failed: {exc}") from exc
    return out
