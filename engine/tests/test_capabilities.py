from pnata_engine.capabilities import detect_capabilities

def test_unknown_semantic_checks_are_not_claimed():
    data = detect_capabilities()
    assert data["semantic_music_detection"] == "UNAVAILABLE"
    assert data["visual_policy_certification"] == "UNAVAILABLE"
