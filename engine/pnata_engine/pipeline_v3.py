"""End-to-end v0.3 project production: validate, render, mix/mux, QC, release gate."""
import json, shutil
from pathlib import Path
from .scene_v3 import validate_scene_project
from .render_v3 import render_video_v3, mux_audio_v3
from .audio_v3 import render_audio_mix
from .qc_v3 import technical_qc, release_gate, write_json_report

def produce_project(project_path, output_path, report_path=None, reviews=None, ffmpeg=None, ffprobe=None):
    project_path=Path(project_path).resolve(); output=Path(output_path).resolve()
    project,root=validate_scene_project(project_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    silent=output.with_name(output.stem+".video-only.mp4")
    render_video_v3(project_path,silent,ffmpeg=ffmpeg)
    if project.get("audio_tracks"):
        wav=output.with_name(output.stem+".mix.wav")
        render_audio_mix(project,root,wav,ffmpeg=ffmpeg,ffprobe=ffprobe)
        mux_audio_v3(silent,wav,output,ffmpeg=ffmpeg)
        wav.unlink(missing_ok=True)
        silent.unlink(missing_ok=True)
        expected_audio=True
    else:
        silent.replace(output)
        expected_audio=False
    technical=technical_qc(output,project,ffprobe=ffprobe,expect_audio=expected_audio)
    gate=release_gate(technical,reviews or {})
    report={"pipeline_version":"0.3","project":str(project_path),"output":str(output),
            "technical_qc":technical,"release_gate":gate,
            "pipeline_status":"complete" if technical["technical_status"]=="pass" else "qc_failed"}
    destination=Path(report_path).resolve() if report_path else output.with_suffix(".qc.json")
    write_json_report(report,destination)
    return report
