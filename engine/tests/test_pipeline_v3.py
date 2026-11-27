import json, shutil, subprocess
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageStat

from pnata_engine.pipeline_v3 import produce_project
from pnata_engine.render_v3 import render_video_v3
from pnata_engine.qc_v3 import REQUIRED_REVIEWS, probe_media


def fixture(tmp_path):
    p = {
        "version": "0.3", "title": "Pipeline test", "width": 160, "height": 90,
        "fps": 24, "duration": 2,
        "policy": {"music": "forbidden", "complete_living_beings": "forbidden", "unseen_depictions": "forbidden"},
        "assets": [],
        "scenes": [
            {"id": "one", "duration": 1, "visual_reviewed_policy_compliant": True, "background": "#101820",
             "layers": [{"id": "title", "type": "text", "start": 0, "end": 1, "text": "P'Nata",
                         "x": .5, "y": .5, "width": .8, "height": .5, "font_size": 20,
                         "overflow": "shrink_to_fit", "min_font_size": 12}],
             "captions": [{"id": "caption", "start": 0, "end": 1, "text": "Test caption",
                           "x": .1, "y": .75, "width": .8, "height": .15, "font_size": 12}]},
            {"id": "two", "duration": 1, "visual_reviewed_policy_compliant": True, "background": "#203040",
             "transition_in": {"type": "dissolve", "duration": .25},
             "layers": [{"id": "shape", "type": "ellipse", "start": 0, "end": 1,
                         "x": .5, "y": .5, "width": .3, "height": .3, "color": "#FFFFFF"}],
             "captions": []}
        ]
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(p), encoding="utf-8")
    return path


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe unavailable")
def test_render_v3_produces_video_with_captions(tmp_path):
    path = fixture(tmp_path)
    out = render_video_v3(path, tmp_path / "render.mp4")
    assert out.is_file() and out.stat().st_size > 1000


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe unavailable")
def test_pipeline_runs_through_qc_but_release_waits_for_reviews(tmp_path):
    path = fixture(tmp_path)
    out = tmp_path / "dist" / "final.mp4"
    report = produce_project(path, out)
    assert out.is_file()
    assert report["technical_qc"]["technical_status"] == "pass"
    assert report["release_gate"]["release_status"] == "blocked"
    assert report["pipeline_status"] == "complete"
    assert out.with_suffix(".qc.json").is_file()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe unavailable")
def test_pipeline_release_requires_all_reviews(tmp_path):
    path = fixture(tmp_path)
    out = tmp_path / "final.mp4"
    reviews = {k: "pass" for k in REQUIRED_REVIEWS}
    report = produce_project(path, out, reviews=reviews)
    assert report["release_gate"]["release_ready"] is True


def test_pipeline_mixes_and_muxes_reviewed_narration(tmp_path):
    import wave
    path = fixture(tmp_path)
    source = tmp_path / "voice.wav"
    with wave.open(str(source), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(b"\x00\x00" * 96000)
    project = json.loads(path.read_text(encoding="utf-8"))
    project["assets"] = [{"id": "voice", "path": "voice.wav", "media_type": "audio",
                          "source": "synthetic test silence", "rights_status": "cleared",
                          "policy_reviewed": True, "audio_category": "narration"}]
    project["audio_tracks"] = [{"id": "narration", "asset_id": "voice", "category": "narration",
                               "start": 0.1, "in_point": 0, "duration": 1.5, "gain_db": -6,
                               "reviewed_non_musical": True, "loop": False}]
    path.write_text(json.dumps(project), encoding="utf-8")
    reviews = {k: "pass" for k in REQUIRED_REVIEWS}
    report = produce_project(path, tmp_path / "with-audio.mp4", reviews=reviews)
    assert report["technical_qc"]["technical_status"] == "pass"
    assert report["technical_qc"]["probe"]["audio_stream_count"] == 1
    assert report["release_gate"]["release_ready"] is True


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe unavailable")
def test_validation_demo_is_six_seconds_and_contains_real_motion(tmp_path):
    project_path = Path(__file__).parents[1] / "examples" / "v03-validation" / "project.json"
    output = render_video_v3(project_path, tmp_path / "animated-demo.mp4")
    probe = probe_media(output)
    assert abs(probe["duration_seconds"] - 6.0) <= 0.15
    assert probe["video"]["width"] == 720
    assert probe["video"]["height"] == 1280
    assert probe["audio_stream_count"] == 0

    frame_a = tmp_path / "frame-a.png"
    frame_b = tmp_path / "frame-b.png"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "0.5",
                    "-i", str(output), "-frames:v", "1", str(frame_a)], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "4.5",
                    "-i", str(output), "-frames:v", "1", str(frame_b)], check=True)
    image_a = Image.open(frame_a).convert("RGB")
    image_b = Image.open(frame_b).convert("RGB")
    difference = ImageStat.Stat(ImageChops.difference(image_a, image_b)).mean
    assert sum(difference) > 0.5, "Rendered frames should differ because animated layers move."


def test_default_font_scales_with_requested_size():
    from PIL import Image, ImageDraw
    from pnata_engine.layout_v3 import _load_font
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    small = draw.textbbox((0, 0), "P'NATA", font=_load_font(18))
    large = draw.textbbox((0, 0), "P'NATA", font=_load_font(72))
    small_height = small[3] - small[1]
    large_height = large[3] - large[1]
    assert large_height >= small_height * 3
