"""CLI for end-to-end v0.3 production."""
import argparse, json
from pathlib import Path
from .pipeline_v3 import produce_project

def main():
 p=argparse.ArgumentParser(description="Validate, render, mix reviewed audio, QC and gate a v0.3 project.")
 p.add_argument("project"); p.add_argument("-o","--output",required=True)
 p.add_argument("--report"); p.add_argument("--reviews",help="JSON object of explicit human review statuses")
 a=p.parse_args()
 reviews=json.loads(Path(a.reviews).read_text(encoding="utf-8")) if a.reviews else {}
 report=produce_project(a.project,a.output,a.report,reviews)
 print(json.dumps({"pipeline_status":report["pipeline_status"],"technical_status":report["technical_qc"]["technical_status"],
                   "release_status":report["release_gate"]["release_status"],"output":report["output"]},indent=2))
 if report["pipeline_status"]!="complete" or report["release_gate"]["release_status"]!="ready": raise SystemExit(2)
if __name__=="__main__": main()
