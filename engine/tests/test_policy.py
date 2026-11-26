import pytest
from pnata_engine.policy import PolicyError, validate_audio_track

def test_music_is_rejected(tmp_path):
    p = tmp_path / "sample.wav"; p.write_bytes(b"not audio")
    with pytest.raises(PolicyError):
        validate_audio_track({"path": str(p), "role": "music", "human_reviewed_non_musical": True})

def test_audio_requires_human_review(tmp_path):
    p = tmp_path / "sample.wav"; p.write_bytes(b"not audio")
    with pytest.raises(PolicyError):
        validate_audio_track({"path": str(p), "role": "voiceover"})
