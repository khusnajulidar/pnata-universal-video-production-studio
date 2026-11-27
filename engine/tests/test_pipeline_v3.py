import json, shutil
import pytest
from pnata_engine.pipeline_v3 import produce_project
from pnata_engine.render_v3 import render_video_v3
from pnata_engine.qc_v3 import REQUIRED_REVIEWS

def fixture(tmp_path):
 p={"version":"0.3","title":"Pipeline test","width":160,"height":90,"fps":24,"duration":2,
 "policy":{"music":"forbidden","complete_living_beings":"forbidden","unseen_depictions":"forbidden"},
 "assets":[],"scenes":[
 {"id":"one","duration":1,"visual_reviewed_policy_compliant":True,"background":"#101820",
  "layers":[{"id":"title","type":"text","start":0,"end":1,"text":"P'Nata","x":.5,"y":.5,"width":.8,"height":.5,"font_size":20,"overflow":"shrink_to_fit","min_font_size":12}],
  "captions":[{"id":"caption","start":0,"end":1,"text":"Test caption","x":.1,"y":.75,"width":.8,"height":.15,"font_size":12}]},
 {"id":"two","duration":1,"visual_reviewed_policy_compliant":True,"background":"#203040","transition_in":{"type":"dissolve","duration":.25},"layers":[{"id":"shape","type":"ellipse","start":0,"end":1,"x":.5,"y":.5,"width":.3,"height":.3,"color":"#FFFFFF"}],"captions":[]} ]}
 path=tmp_path/"project.json"; path.write_text(json.dumps(p),encoding="utf-8"); return path

@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),reason="FFmpeg/FFprobe unavailable")
def test_render_v3_produces_video_with_captions(tmp_path):
 path=fixture(tmp_path); out=render_video_v3(path,tmp_path/"render.mp4")
 assert out.is_file() and out.stat().st_size>1000

@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),reason="FFmpeg/FFprobe unavailable")
def test_pipeline_runs_through_qc_but_release_waits_for_reviews(tmp_path):
 path=fixture(tmp_path); out=tmp_path/"dist"/"final.mp4"
 report=produce_project(path,out)
 assert out.is_file()
 assert report["technical_qc"]["technical_status"]=="pass"
 assert report["release_gate"]["release_status"]=="blocked"
 assert report["pipeline_status"]=="complete"
 assert out.with_suffix(".qc.json").is_file()

@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),reason="FFmpeg/FFprobe unavailable")
def test_pipeline_release_requires_all_reviews(tmp_path):
 path=fixture(tmp_path); out=tmp_path/"final.mp4"
 reviews={k:"pass" for k in REQUIRED_REVIEWS}
 report=produce_project(path,out,reviews=reviews)
 assert report["release_gate"]["release_ready"] is True
