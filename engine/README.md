# P'Nata Video Engine 0.1.0

Starter production engine using Python, Pillow, FFmpeg and FFprobe.

## Current capabilities
- JSON project configuration and ordered scene timeline.
- Typography-first still scenes; optional background images require human visual-policy review.
- H.264 MP4 rendering, configurable dimensions and frame rate.
- Optional narration, speech, non-musical SFX and genuinely non-musical ambience.
- Audio start offsets and volume; audio is padded to the video duration.
- FFprobe metadata report and runtime capability inventory.
- Hard policy gates reject music-like roles and unreviewed audio/image assets.

## Install
Python 3.10+, FFmpeg and FFprobe are required.
```bash
python -m pip install -e '.[validation]'
```

## Run
```bash
pnata-render examples/minimal/project.json -o dist/final.mp4 --qc dist/qc.json
pnata-capabilities
```

## Honest limitations
v0.1 is a typography/still-scene renderer with hard cuts, not a nonlinear editor. It has no keyframed animation, transitions, subtitles, multi-layer compositor, semantic music detection, or automated certification that visuals contain no complete living beings. Human review declarations are workflow gates, not machine proof. QC explicitly leaves semantic audio and visual review incomplete.
