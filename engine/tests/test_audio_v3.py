import shutil, subprocess, wave
import pytest
from pnata_engine.audio_v3 import AudioV3Error, build_audio_filter, probe_audio_asset, render_audio_mix

def project(tracks=None): return {"duration":4,"audio_tracks":tracks or []}
def track(**kw):
    d={"id":"voice","category":"narration","start":.5,"in_point":.25,"duration":2,"gain_db":-3,"fade_in":.2,"fade_out":.3,"reviewed_non_musical":True}
    d.update(kw)
    return d

def test_exact_duration_silence_graph():
    assert build_audio_filter(project())=="anullsrc=r=48000:cl=stereo,atrim=duration=4.000000000[mix]"
def test_filter_trim_gain_fades_offset():
    g=build_audio_filter(project([track()]))
    for x in ["atrim=start=0.250000000:duration=2.000000000","volume=-3.000000dB","afade=t=in","afade=t=out","adelay=500:all=1","amix=inputs=1:duration=longest:normalize=0"]: assert x in g
@pytest.mark.parametrize("category",["music","instrumental","unknown"])
def test_reject_forbidden_category(category):
    with pytest.raises(AudioV3Error,match="category"): build_audio_filter(project([track(category=category)]))
def test_requires_human_review():
    with pytest.raises(AudioV3Error,match="review"): build_audio_filter(project([track(reviewed_non_musical=False)]))
def test_rejects_loop():
    with pytest.raises(AudioV3Error,match="looping"): build_audio_filter(project([track(loop=True)]))
def test_rejects_long_fades():
    with pytest.raises(AudioV3Error,match="fades"): build_audio_filter(project([track(fade_in=1.5,fade_out=1)]))
def test_rejects_project_overrun():
    with pytest.raises(AudioV3Error,match="exceeds project"): build_audio_filter(project([track(start=3)]))
def test_rejects_gain():
    with pytest.raises(AudioV3Error,match="gain"): build_audio_filter(project([track(gain_db=13)]))
def test_rejects_nan():
    with pytest.raises(AudioV3Error,match="finite"): build_audio_filter(project([track(gain_db=float("nan"))]))
def test_probe_rejects_video_without_audio(tmp_path):
    ffprobe=shutil.which("ffprobe"); ffmpeg=shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg: pytest.skip("FFmpeg/FFprobe unavailable")
    p=tmp_path/"silent.mp4"
    subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-f","lavfi","-i","color=c=black:s=32x32:d=1","-an","-c:v","libx264","-pix_fmt","yuv420p",str(p)],check=True)
    with pytest.raises(AudioV3Error,match="No audio stream"): probe_audio_asset(p)
def test_render_exact_duration_silence(tmp_path):
    if not shutil.which("ffmpeg"): pytest.skip("FFmpeg unavailable")
    out=render_audio_mix(project(),tmp_path,tmp_path/"silence.wav")
    with wave.open(str(out),"rb") as w:
        assert w.getframerate()==48000 and w.getnchannels()==2
        assert abs(w.getnframes()/w.getframerate()-4)<.01
