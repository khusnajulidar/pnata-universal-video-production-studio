"""Command line entry point for v0.3 technical QC and release gating."""
import argparse, json
from pathlib import Path
from .qc_v3 import technical_qc, release_gate, write_json_report

def main():
 p=argparse.ArgumentParser(description="Run FFprobe technical QC and P'Nata human-reviewed release gate.")
 p.add_argument("media",help="Rendered video/audio container to inspect")
 p.add_argument("--project",required=True,help="v0.3 project JSON with expected canvas/FPS/duration")
 p.add_argument("--output",required=True,help="Combined QC and release-gate JSON output")
 g=p.add_mutually_exclusive_group()
 g.add_argument("--expect-audio",action="store_true",help="Require at least one audio stream")
 g.add_argument("--expect-no-audio",action="store_true",help="Require no audio streams")
 p.add_argument("--reviews",help="JSON object containing human review statuses: pass/fail/pending")
 args=p.parse_args()
 project=json.loads(Path(args.project).read_text(encoding="utf-8"))
 reviews=json.loads(Path(args.reviews).read_text(encoding="utf-8")) if args.reviews else {}
 expected=True if args.expect_audio else False if args.expect_no_audio else None
 technical=technical_qc(args.media,project,expect_audio=expected)
 gate=release_gate(technical,reviews)
 report={"technical_qc":technical,"release_gate":gate}
 write_json_report(report,args.output)
 print(json.dumps({"technical_status":technical["technical_status"],"release_status":gate["release_status"],"report":str(Path(args.output).resolve())},indent=2))
 if technical["technical_status"]!="pass" or gate["release_status"]!="ready": raise SystemExit(2)

if __name__=="__main__": main()
