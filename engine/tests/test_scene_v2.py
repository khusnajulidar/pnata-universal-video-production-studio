import json
import pytest
from pnata_engine.scene_v2 import evaluate_keyframes, load_scene_project, SceneV2Error

def test_linear_interpolation():
    frames=[{"time":0,"value":0},{"time":2,"value":10}]
    assert evaluate_keyframes(frames,1,99)==5

def test_ease_in_interpolation():
    frames=[{"time":0,"value":0,"ease":"ease_in"},{"time":2,"value":8}]
    assert evaluate_keyframes(frames,1,0)==2

def test_clamps_outside_keyframes():
    frames=[{"time":1,"value":3},{"time":2,"value":7}]
    assert evaluate_keyframes(frames,0,0)==3
    assert evaluate_keyframes(frames,5,0)==7

def test_rejects_unknown_easing():
    with pytest.raises(SceneV2Error):
        evaluate_keyframes([{"time":0,"value":0,"ease":"bounce"},{"time":1,"value":1}],.5,0)

def test_fixture_loads():
    data,_=load_scene_project("examples/v02-motion/project.json")
    assert len(data["scenes"])==2

def test_policy_flags_are_mandatory(tmp_path):
    data={"title":"x","width":100,"height":100,"fps":24,"duration":1,
          "scenes":[{"duration":1,"visual_reviewed_policy_compliant":True,"layers":[]}],
          "policy":{"music":"allowed","complete_living_beings":"forbidden"}}
    p=tmp_path/"p.json"; p.write_text(json.dumps(data))
    with pytest.raises(SceneV2Error): load_scene_project(p)
