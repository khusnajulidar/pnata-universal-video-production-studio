# P'Nata Video Engine — v0.1 baseline, v0.2 renderer, v0.3 validation/layout/timeline

The engine keeps separate, explicit execution paths. v0.1 and v0.2 remain available; v0.3 currently adds strict project validation and reusable typography/image layout primitives.

## v0.1 baseline renderer
- Typography/still scenes with hard cuts.
- Optional reviewed speech, non-musical SFX and genuinely non-musical ambience.
- FFmpeg H.264 output and FFprobe technical report.
- Command: `pnata-render`.

## v0.2 animated 2D scene renderer
- Ordered scenes and independently positioned text, rectangle, ellipse, line, and reviewed still-image layers.
- Numeric keyframes for x, y, scale, opacity, rotation; linear/ease-in/ease-out/ease-in-out.
- Cut and dissolve transitions; flexible canvas/FPS/duration.
- Command: `pnata-render-v2`.
- Silent-only; it does not mix audio.

## v0.3 validation — Milestone A
- JSON Schema 2020-12 manifest and strict Python validator.
- Checks required policy declarations, asset provenance/rights/review declarations, file existence and project-relative path safety.
- Rejects unclassified or prohibited audio categories, embedded audio in visual assets, and unreviewed audio tracks.
- Checks scene/layer timing, references, keyframe properties, and basic audio-track timing.
- Command: `pnata-validate-v3`.
- Validation does not render.

## v0.3 layout primitives — Milestone B (locally verified: 30 tests passed)
- `pnata_engine.layout_v3.layout_text`: text wrapping, paragraph breaks, horizontal/vertical alignment, line spacing, padding, and explicit overflow modes.
- Overflow modes: `error`, `clip` (reports clipping), and `shrink_to_fit` (requires a minimum font size).
- Font lookup follows caller-supplied paths and falls back to Pillow's default font.
- `draw_text_layout`: draws a measured text layout.
- `fit_image`: deterministic `contain`, `cover` with normalized crop anchor, and explicit `stretch`.
- Tests: `tests/test_layout_v3.py`.
- These are primitives only; a complete v0.3 scene renderer has not yet been integrated.

## v0.3 timeline and captions — Milestone C (implementation added; verification pending)
- Sequential scene windows mapped to global project time.
- Half-open layer visibility windows [start, end) and deterministic frame quantization.
- Per-scene timed caption cues mapped to global time.
- Configurable normalized safe margins (default 5% on each edge); captions outside the safe area are rejected by validation.
- Module: `pnata_engine.timeline_v3`; validator integrates caption/safe-margin checks.
- Caption rendering and subtitle export are not included yet.

## v0.3 reviewed audio — Milestone D (implementation added; verification pending)
- Module: `pnata_engine.audio_v3`; narration, genuinely non-musical SFX, and genuinely non-musical natural ambience only.
- Source trim, timeline offset, gain, fades, deterministic overlap mix, exact-duration silence; FFprobe checks source audio stream and trim bounds.
- Output: 48 kHz stereo PCM WAV. Standalone mix only; video mux integration is not included.
- Human review flags are attestations, not a semantic music detector. Ambiguous audio must be excluded.

## v0.3 technical QC and release gate — Milestone E (implementation added; verification pending)
- `pnata_engine.qc_v3.probe_media`: FFprobe inventory of video/audio streams, dimensions, frame rate, codecs, sample rate, channels, duration, and file size.
- `technical_qc`: compares one video stream, dimensions, FPS, container duration, and optional expected audio-stream presence against the project specification.
- `release_gate`: blocks release unless technical QC passes and all seven human reviews explicitly say `pass` (content accuracy, rights/provenance, visual policy, audio policy, visual quality, audio quality, final playback).
- CLI: `pnata-qc-v3 output.mp4 --project project.json --output dist/qc.json --expect-no-audio [--reviews reviews.json]`.
- Technical QC cannot detect music semantically, certify visual policy, verify rights, or replace human playback. Loudness/true-peak analysis is not included.

## Install
Python 3.10+, Pillow, and FFmpeg are needed for rendering. FFprobe is recommended. JSON Schema validation is included in the validation extra.
```bash
python -m pip install -e ".[validation]"
```

## Run
```bash
pnata-render examples/minimal/project.json -o dist/v01.mp4 --qc dist/v01-qc.json
pnata-render-v2 examples/v02-motion/project.json -o dist/v02.mp4 --qc dist/v02-qc.json
pnata-validate-v3 examples/v03-validation/project.json
pnata-capabilities
pytest -q
```

## Scene formats
- [v0.2 format](SCENE_FORMAT_V0.2.md) and [v0.2 schema](schema/scene-project-v0.2.schema.json).
- [v0.3 Milestones A–C format](SCENE_FORMAT_V0.3.md) and [v0.3 schema](schema/scene-project-v0.3.schema.json).
- [v0.3 implementation specification](V0.3_SPEC.md).

## Backend boundaries
The v0.2 backend is a deterministic 2D raster compositor, not a full nonlinear editor. It does not provide 3D cameras/lighting, advanced particles, complex masks, arbitrary footage editing, audio mixing, semantic music detection, or automated visual-policy certification. Cinematic footage, documentary archive editing, advanced motion graphics, complex presentations, and audio-led projects may require another verified backend. Never silently flatten unsupported instructions into still frames.

## Hard P'Nata policy
- No music, without exception.
- Audio allowed only when explicitly reviewed as narration, genuinely non-musical SFX, or genuinely non-musical natural/environmental ambience; silence is valid.
- No complete depictions of humans or animals, including silhouettes or fragments arranged to imply a complete figure.
- No figurative depictions of Allah, prophets, angels, or unseen matters.
- Human review flags are workflow declarations, not machine certification. Final visuals and all audible assets still require human review.
- v0.2 accepts no audio tracks. v0.3 validation rejects music/unclassified categories and unreviewed audio; it does not semantically detect music.

## QC and status discipline
FFprobe technical QC does not establish narrative, factual, rights, audio-semantic, or visual-policy approval. Do not describe a feature as implemented, tested, or production-ready until it has actually been executed and reviewed.
