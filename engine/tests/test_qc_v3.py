import shutil, subprocess
import pytest
from pnata_engine.qc_v3 import QCV3Error, probe_media, technical_qc, release_gate, REQUIRED_REVIEWS
def make_video(path,duration="2",size="160x90",fps="24",audio=False):
 ffmpeg=shutil.which("ffmpeg")
 if not ffmpeg: pytest.skip("FFmpeg unavailable")
 args=[ffmpeg,"-hide_banner","-loglevel","error","-y","-f","lavfi","-i",f"color=c=black:s={size}:r={fps}:d={duration}"]
 if audio: args += ["-f","lavfi","-i",f"anullsrc=r=48000:cl=stereo:d={duration}"]
 args += ["-c:v","libx264","-pix_fmt","yuv420p"]
 if audio: args += ["-c:a","aac","-shortest"]
 args += [str(path)]; subprocess.run(args,check=True)
def spec(): return {"width":160,"height":90,"fps":24,"duration":2}
def test_probe_metadata(tmp_path):
 p=tmp_path/"v.mp4"; make_video(p); d=probe_media(p)
 assert d["video"]["width"]==160 and d["video"]["height"]==90 and d["audio_stream_count"]==0
def test_probe_missing_file(tmp_path):
 with pytest.raises(QCV3Error,match="not found"): probe_media(tmp_path/"missing.mp4")
def test_silent_video_technical_pass(tmp_path):
 p=tmp_path/"v.mp4"; make_video(p); r=technical_qc(p,spec(),expect_audio=False)
 assert r["technical_status"]=="pass" and all(x["status"]=="pass" for x in r["checks"])
def test_wrong_dimensions_fail(tmp_path):
 p=tmp_path/"v.mp4"; make_video(p,size="128x72"); r=technical_qc(p,spec(),expect_audio=False)
 assert r["technical_status"]=="fail" and next(x for x in r["checks"] if x["name"]=="width")["status"]=="fail"
def test_audio_presence_checked(tmp_path):
 p=tmp_path/"v.mp4"; make_video(p,audio=True)
 assert technical_qc(p,spec(),expect_audio=True)["technical_status"]=="pass"
 assert technical_qc(p,spec(),expect_audio=False)["technical_status"]=="fail"
def test_release_gate_blocks_pending():
 r=release_gate({"technical_status":"pass"},{})
 assert r["release_status"]=="blocked" and set(r["pending_reviews"])==set(REQUIRED_REVIEWS)
def test_release_gate_requires_technical_and_all_human_pass():
 reviews={k:"pass" for k in REQUIRED_REVIEWS}
 assert release_gate({"technical_status":"pass"},reviews)["release_ready"] is True
 assert release_gate({"technical_status":"fail"},reviews)["release_ready"] is False
def test_release_gate_blocks_failed_review():
 reviews={k:"pass" for k in REQUIRED_REVIEWS}; reviews["audio_policy"]="fail"
 r=release_gate({"technical_status":"pass"},reviews)
 assert r["release_status"]=="blocked" and r["failed_reviews"]==["audio_policy"]
def test_unknown_review_value_is_pending():
 reviews={k:"pass" for k in REQUIRED_REVIEWS}; reviews["visual_policy"]="approved"
 r=release_gate({"technical_status":"pass"},reviews)
 assert not r["release_ready"] and "visual_policy" in r["pending_reviews"]

def test_unspecified_audio_presence_is_incomplete_not_release_pass(tmp_path):
    p=tmp_path/"v.mp4"; make_video(p)
    assert technical_qc(p,spec())["technical_status"]=="incomplete"
def test_optional_codec_expectation_is_checked(tmp_path):
    p=tmp_path/"v.mp4"; make_video(p)
    project=spec(); project["video_codec"]="mpeg4"
    assert technical_qc(p,project,expect_audio=False)["technical_status"]=="fail"
