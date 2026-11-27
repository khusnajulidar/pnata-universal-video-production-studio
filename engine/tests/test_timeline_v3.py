import pytest
from pnata_engine.timeline_v3 import (
    TimelineV3Error, active_layers_at, caption_cues, frame_to_seconds,
    scene_windows, seconds_to_frame, validate_timeline,
)


def project():
    return {
        "duration": 5, "fps": 24,
        "scenes": [
            {"id": "intro", "duration": 2,
             "layers": [{"id": "title", "start": 0.5, "end": 1.5}],
             "captions": [{"id": "c1", "start": 0.25, "end": 1.25,
                           "text": "Opening", "x": 0.1, "y": 0.8,
                           "width": 0.8, "height": 0.1, "font_size": 28}]},
            {"id": "main", "duration": 3,
             "layers": [{"id": "body", "start": 0, "end": 3}],
             "captions": [{"id": "c2", "start": 1, "end": 2,
                           "text": "Main", "x": 0.1, "y": 0.8,
                           "width": 0.8, "height": 0.1, "font_size": 28}]},
        ],
    }


def test_scene_windows_are_sequential():
    windows = scene_windows(project())
    assert [(w.start, w.end) for w in windows] == [(0, 2), (2, 5)]


def test_active_layer_uses_global_time_and_half_open_interval():
    p = project()
    assert active_layers_at(p, 0.5)[0]["layer"]["id"] == "title"
    assert active_layers_at(p, 1.5) == ()
    assert active_layers_at(p, 2.0)[0]["layer"]["id"] == "body"


def test_timeline_outside_project_is_empty():
    assert active_layers_at(project(), 5) == ()


def test_caption_cues_are_mapped_to_global_time():
    cues = caption_cues(project())
    assert (cues[0]["global_start"], cues[0]["global_end"]) == (0.25, 1.25)
    assert (cues[1]["global_start"], cues[1]["global_end"]) == (3.0, 4.0)


def test_frame_quantization_is_deterministic():
    assert seconds_to_frame(1.0, 24) == 24
    assert seconds_to_frame(0.5, 24) == 12
    assert frame_to_seconds(48, 24) == 2


def test_reject_caption_outside_scene():
    p = project()
    p["scenes"][0]["captions"][0]["end"] = 2.1
    with pytest.raises(TimelineV3Error, match="Invalid caption time"):
        validate_timeline(p)


def test_reject_caption_outside_safe_margins():
    p = project()
    p["scenes"][0]["captions"][0]["x"] = 0.01
    with pytest.raises(TimelineV3Error, match="safe margins"):
        validate_timeline(p)


def test_reject_duplicate_caption_ids_per_scene():
    p = project()
    p["scenes"][0]["captions"].append(dict(p["scenes"][0]["captions"][0]))
    with pytest.raises(TimelineV3Error, match="Duplicate caption"):
        validate_timeline(p)


def test_reject_invalid_safe_margin_sum():
    p = project()
    p["safe_margins"] = {"left": 0.6, "right": 0.5}
    with pytest.raises(TimelineV3Error, match="Opposing safe margins"):
        validate_timeline(p)
