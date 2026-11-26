from pnata_engine.project import load_project

def test_example_project_loads():
    data, _ = load_project("examples/minimal/project.json")
    assert data["width"] == 1080 and len(data["scenes"]) == 2
