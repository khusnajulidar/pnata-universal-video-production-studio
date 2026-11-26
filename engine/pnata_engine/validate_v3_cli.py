"""CLI for validating P'Nata v0.3 project files."""
import argparse,sys
from .scene_v3 import SceneV3Error,validate_scene_project
def main():
    parser=argparse.ArgumentParser(description="Validate a P'Nata v0.3 scene project.")
    parser.add_argument("project"); args=parser.parse_args()
    try: project,_=validate_scene_project(args.project)
    except SceneV3Error as exc:
        print(f"INVALID: {exc}",file=sys.stderr); raise SystemExit(2)
    print(f"VALID: {project['title']} ({project['duration']}s)")
    print("No rendering was performed; human visual/audio review is still required.")
if __name__=="__main__": main()
