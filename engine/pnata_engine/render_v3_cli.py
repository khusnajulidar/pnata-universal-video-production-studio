"""Standalone CLI for the v0.3 visual renderer."""
import argparse
from .render_v3 import render_video_v3
def main():
    parser=argparse.ArgumentParser(description="Render validated v0.3 2D visuals and captions to silent H.264 MP4.")
    parser.add_argument("project")
    parser.add_argument("-o","--output",required=True)
    args=parser.parse_args()
    print(render_video_v3(args.project,args.output))
if __name__=="__main__": main()
