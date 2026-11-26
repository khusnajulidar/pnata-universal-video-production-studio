# P'Nata Video Engine — v0.1 baseline + v0.2 scene renderer

The engine now has two deliberately distinct render paths.

## v0.1 baseline renderer
- Typography/still scenes with hard cuts.
- Optional reviewed speech, non-musical SFX and genuinely non-musical ambience.
- FFmpeg H.264 output and FFprobe technical report.
- Existing command: `pnata-render`.

## v0.2 animated 2D scene renderer
- Ordered scenes and multiple independently positioned layers.
- Layer types: text, rectangle, ellipse, line, and reviewed still image.
- Numeric keyframes for x, y, scale, opacity, and rotation.
- Deterministic interpolation: linear, ease-in, ease-out, ease-in-out.
- Scene transitions: hard cut and dissolve.
- Flexible canvas dimensions, frame rate, duration, H.264 encoding.
- Explicit backend capability registry.
- New command: `pnata-render-v2`.
- v0.2 path is silent-only. It does not mix audio; narration/SFX remain a separate reviewed production stage.

## Install
Python 3.10+, Pillow and FFmpeg are required. FFprobe is recommended for technical QC.
```bash
python -m pip install -e '.[validation]'
```

## Run
```bash
pnata-render examples/minimal/project.json -o dist/v01.mp4 --qc dist/v01-qc.json
pnata-render-v2 examples/v02-motion/project.json -o dist/v02.mp4 --qc dist/v02-qc.json
pnata-capabilities
```

## Scene format
See [SCENE_FORMAT_V0.2.md](SCENE_FORMAT_V0.2.md) and the JSON Schema at [schema/scene-project-v0.2.schema.json](schema/scene-project-v0.2.schema.json).

## Backend boundaries — read before selecting
The v0.2 backend is a deterministic **2D raster compositor**, not a full nonlinear editor. It does not provide 3D cameras/lighting, advanced particles, complex masks, footage editing, automatic subtitle timing, audio mixing, semantic music detection, or automated visual-policy certification. It is suitable for typography-led motion, simple infographic/explainer sequences, abstract visual essays, and restrained 2D compositions when the brief fits its capability envelope.

Cinematic footage, documentary archive editing, advanced motion graphics, complex presentations, and audio-led projects may require another backend. The orchestrator must detect the required capabilities, select a confirmed compatible backend, or disclose that the requested production cannot yet be completed at the required quality. Never silently flatten unsupported instructions into still frames.

## Policy and QC
- Both hard P'Nata policy flags are mandatory: music forbidden; complete depictions of living beings forbidden.
- Every scene must carry a human visual-policy review declaration. Still-image assets require their own review declaration.
- These declarations are process gates, not machine proof. A human must inspect final rendered frames, not merely trust metadata.
- v0.2 renderer accepts no audio tracks. No audio is safer than accidentally passing unreviewed audio.
- FFprobe technical QC does not establish narrative, factual, rights, audio-semantic, or visual-policy approval.
