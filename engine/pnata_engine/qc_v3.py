"""Technical media QC and human-reviewed release gate for P'Nata."""
import json, math, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
class QCV3Error(ValueError): pass
REQUIRED_REVIEWS=("content_accuracy","rights_and_provenance","visual_policy","audio_policy","visual_quality","audio_quality","final_playback")
def _number(value,label):
 try: result=float(value)
 except (TypeError,ValueError) as exc: raise QCV3Error(f"Invalid {label}.") from exc
 if not math.isfinite(result): raise QCV3Error(f"Invalid {label}.")
 return result
def _fraction(value):
 if not value or value in {"0/0","N/A"}: return None
 try:
  a,b=value.split("/",1); result=float(a)/float(b)
  return result if math.isfinite(result) else None
 except (ValueError,AttributeError,ZeroDivisionError): return None
def probe_media(path,ffprobe=None):
 binary=ffprobe or shutil.which("ffprobe")
 if not binary: raise QCV3Error("FFprobe unavailable.")
 media=Path(path).resolve()
 if not media.is_file(): raise QCV3Error(f"Media file not found: {media}")
 try: p=subprocess.run([binary,"-v","error","-show_streams","-show_format","-of","json",str(media)],check=True,capture_output=True,text=True)
 except (OSError,subprocess.CalledProcessError) as exc: raise QCV3Error(f"FFprobe failed: {exc}") from exc
 try: data=json.loads(p.stdout)
 except json.JSONDecodeError as exc: raise QCV3Error("FFprobe returned invalid JSON.") from exc
 streams=data.get("streams",[]); videos=[s for s in streams if s.get("codec_type")=="video"]; audios=[s for s in streams if s.get("codec_type")=="audio"]; fmt=data.get("format",{})
 dur=_number(fmt.get("duration"),"container duration") if fmt.get("duration") is not None else None
 v=videos[0] if videos else {}
 return {"file":str(media),"file_size_bytes":media.stat().st_size,"container":fmt.get("format_name"),"duration_seconds":dur,
 "video_stream_count":len(videos),"audio_stream_count":len(audios),
 "video":None if not videos else {"codec":v.get("codec_name"),"width":v.get("width"),"height":v.get("height"),"frame_rate":_fraction(v.get("avg_frame_rate") or v.get("r_frame_rate")),"pixel_format":v.get("pix_fmt"),"duration_seconds":_number(v.get("duration"),"video duration") if v.get("duration") else None},
 "audio":[{"codec":s.get("codec_name"),"sample_rate":int(s["sample_rate"]) if s.get("sample_rate") else None,"channels":s.get("channels"),"duration_seconds":_number(s.get("duration"),"audio duration") if s.get("duration") else None} for s in audios]}
def technical_qc(media_path,project,ffprobe=None,expect_audio=None,duration_tolerance=.15,fps_tolerance=.02):
 probe=probe_media(media_path,ffprobe); checks=[]
 def add(name,ok,actual=None,expected=None,detail=None): checks.append({"name":name,"status":"pass" if ok else "fail","actual":actual,"expected":expected,"detail":detail})
 v=probe["video"]; add("video_stream_present",probe["video_stream_count"]==1,probe["video_stream_count"],1)
 if v:
  add("width",v["width"]==project["width"],v["width"],project["width"]); add("height",v["height"]==project["height"],v["height"],project["height"])
  fps=v["frame_rate"]; target=float(project["fps"]); add("frame_rate",fps is not None and abs(fps-target)<=fps_tolerance,fps,target)
 else:
  add("width",False,None,project["width"],"No video stream."); add("height",False,None,project["height"],"No video stream."); add("frame_rate",False,None,project["fps"],"No video stream.")
 target=_number(project["duration"],"project duration"); actual=probe["duration_seconds"]
 add("duration",actual is not None and abs(actual-target)<=duration_tolerance,actual,target,f"Tolerance ±{duration_tolerance:.3f}s.")
 if expect_audio is None: checks.append({"name":"audio_stream_presence","status":"not_checked","actual":probe["audio_stream_count"],"expected":"unspecified","detail":"Specify expected audio presence for release QC."})
 else:
  present=probe["audio_stream_count"]>0; add("audio_stream_presence",present is bool(expect_audio),present,bool(expect_audio))
 passed=all(c["status"]=="pass" for c in checks if c["status"]!="not_checked")
 return {"report_version":"1.0","created_at":datetime.now(timezone.utc).isoformat(),"technical_status":"pass" if passed else "fail","probe":probe,"checks":checks,
 "limitations":["No semantic music detection.","No visual content or living-being policy certification.","No rights verification.","No loudness/true-peak certification.","Technical QC cannot replace full human playback review."]}
def release_gate(technical_report,human_reviews):
 reviews={}
 for key in REQUIRED_REVIEWS:
  value=human_reviews.get(key,"pending") if isinstance(human_reviews,dict) else "pending"
  reviews[key]=value if value in {"pass","fail","pending"} else "pending"
 pending=[k for k,v in reviews.items() if v=="pending"]; failed=[k for k,v in reviews.items() if v=="fail"]
 technical=technical_report.get("technical_status")=="pass"; ready=technical and not pending and not failed
 return {"gate_version":"1.0","release_status":"ready" if ready else "blocked","technical_status":"pass" if technical else "fail","human_reviews":reviews,"pending_reviews":pending,"failed_reviews":failed,"release_ready":ready,
 "warning":"Human review values are attestations. The engine cannot semantically certify music-free audio, visual policy compliance, factual correctness, or rights."}
def write_json_report(report,path):
 out=Path(path); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return out
