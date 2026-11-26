import argparse
from pathlib import Path
from .render import render_project
from .qc import write_qc_report

def main():
    parser = argparse.ArgumentParser(prog="pnata-render")
    parser.add_argument("project")
    parser.add_argument("-o", "--output", default="dist/final.mp4")
    parser.add_argument("--qc")
    args = parser.parse_args()
    output = render_project(args.project, args.output)
    print(f"Rendered: {output}")
    if args.qc:
        report = write_qc_report(output, args.qc)
        print(f"QC report: {Path(args.qc).resolve()} ({report['duration']:.2f}s)")

if __name__ == "__main__": main()
