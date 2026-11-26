import json
import pytest
from pnata_engine.scene_v3 import SceneV3Error,validate_scene_project

def base():
 return {"version":"0.3","title":"Validation fixture","width":720,"height":1280,"fps":24,"duration":2,
 "policy":{"music":"forbidden","complete_living_beings":"forbidden","unseen_depictions":"forbidden"},
 "assets":[],"scenes":[{"id":"s1","duration":2,"visual_reviewed_policy_compliant":True,"layers":[]}],"audio_tracks":[]}
def write(tmp,data):
 p=tmp/"project.json"; p.write_text(json.dumps(data),encoding="utf-8"); return p
def test_valid_minimal(tmp_path):
 p,_=validate_scene_project(write(tmp_path,base())); assert p["version"]=="0.3"
def test_reject_music_policy(tmp_path):
 d=base(); d["policy"]["music"]="allowed"
 with pytest.raises(SceneV3Error,match="Schema error"): validate_scene_project(write(tmp_path,d))
def test_reject_visual_review_false(tmp_path):
 d=base(); d["scenes"][0]["visual_reviewed_policy_compliant"]=False
 with pytest.raises(SceneV3Error): validate_scene_project(write(tmp_path,d))
def test_reject_music_audio_category(tmp_path):
 d=base(); d["assets"]=[{"id":"a","path":"music.wav","media_type":"audio","source":"test","rights_status":"cleared","policy_reviewed":True,"audio_category":"music"}]
 with pytest.raises(SceneV3Error): validate_scene_project(write(tmp_path,d))
def test_reject_unreviewed_audio_track(tmp_path):
 d=base(); d["assets"]=[{"id":"a","path":"voice.wav","media_type":"audio","source":"recorded","rights_status":"cleared","policy_reviewed":True,"audio_category":"narration"}]
 d["audio_tracks"]=[{"id":"t","asset_id":"a","category":"narration","start":0,"duration":1,"gain_db":0,"reviewed_non_musical":False}]
 with pytest.raises(SceneV3Error): validate_scene_project(write(tmp_path,d))
def test_reject_missing_asset(tmp_path):
 d=base(); d["assets"]=[{"id":"i","path":"missing.png","media_type":"image","source":"test","rights_status":"cleared","policy_reviewed":True,"contains_embedded_audio":False}]
 with pytest.raises(SceneV3Error,match="Asset file not found"): validate_scene_project(write(tmp_path,d))
def test_reject_path_traversal(tmp_path):
 outside=tmp_path.parent/"outside.txt"; outside.write_text("x")
 d=base(); d["assets"]=[{"id":"i","path":"../outside.txt","media_type":"image","source":"test","rights_status":"cleared","policy_reviewed":True,"contains_embedded_audio":False}]
 with pytest.raises(SceneV3Error,match="escapes"): validate_scene_project(write(tmp_path,d))
def test_reject_layer_outside_scene(tmp_path):
 d=base(); d["scenes"][0]["layers"]=[{"id":"t","type":"text","start":0,"end":3,"text":"hi","width":0.8,"height":0.2,"font_size":40}]
 with pytest.raises(SceneV3Error,match="Invalid layer time"): validate_scene_project(write(tmp_path,d))
def test_reject_uncleared_rights(tmp_path):
 d=base(); d["assets"]=[{"id":"i","path":"x.png","media_type":"image","source":"unknown","rights_status":"unknown","policy_reviewed":True,"contains_embedded_audio":False}]
 with pytest.raises(SceneV3Error): validate_scene_project(write(tmp_path,d))
def test_reject_unclassified_audio(tmp_path):
 d=base(); d["assets"]=[{"id":"a","path":"voice.wav","media_type":"audio","source":"recorded","rights_status":"cleared","policy_reviewed":True}]
 with pytest.raises(SceneV3Error): validate_scene_project(write(tmp_path,d))
