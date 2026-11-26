import shutil
import pytest
from pnata_engine.render_v2 import render_scene_project

@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg not installed")
def test_v02_fixture_renders_h264_mp4(tmp_path):
    output=tmp_path/"fixture.mp4"
    render_scene_project("examples/v02-motion/project.json",output)
    assert output.is_file()
    assert output.stat().st_size > 1000
    if shutil.which("ffprobe"):
        import json, subprocess
        result=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate",
          "-show_entries","format=duration","-of","json",str(output)],capture_output=True,text=True,check=True)
        probe=json.loads(result.stdout)
        assert any(s.get("codec_name")=="h264" for s in probe["streams"])
        assert any(s.get("width")==720 and s.get("height")==1280 for s in probe["streams"])
