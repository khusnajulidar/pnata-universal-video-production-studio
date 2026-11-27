# Scene Project Format v0.3 — Milestones A, B, and C

The v0.3 manifest is validated metadata. Milestone B adds reusable Pillow layout primitives; it does not yet provide a complete v0.3 video renderer.

## Project
Required: `version: "0.3"`, title, canvas width/height, fps, duration, policy, assets, scenes. Optional audio_tracks defaults to empty.

## Hard policy
Required fixed values: music, complete_living_beings, unseen_depictions = `forbidden`.

## Assets
Each asset has a unique id, project-relative path, media_type, source, rights_status=`cleared`, and policy_reviewed=true. Files must exist under the project directory; path traversal is rejected. Audio assets must declare narration, sfx, or natural_ambience. Visual assets with embedded audio are rejected. These are human workflow attestations, not automated rights or semantic certification.

## Scenes and layers
Scenes have unique IDs, positive duration, visual_reviewed_policy_compliant=true, and layers. Layer times are seconds relative to the scene. Text requires text, box dimensions, and font size. Images reference declared image assets and choose contain/cover/stretch. Keyframes are limited to x/y/scale/opacity/rotation.

## Typography layout primitives — Milestone B
`pnata_engine.layout_v3.layout_text` calculates wrapped lines, horizontal and vertical alignment, line spacing, padding, and explicit overflow handling:
- `error`: fail when content does not fit (default).
- `clip`: return only visible lines and mark the layout as clipped.
- `shrink_to_fit`: reduce font size only down to the required `min_font_size`; otherwise fail.
Font paths are tried in declared order. If none resolve, Pillow's default font is used. The caller should provide reviewed/licensed font assets and paths.

`draw_text_layout` draws the measured layout. `fit_image` implements:
- `contain`: preserves the complete image and adds transparent padding.
- `cover`: fills the target box and crops deterministically using normalized anchor coordinates.
- `stretch`: changes aspect ratio only when explicitly requested.

These are layout primitives, not visual review or policy certification. Complex shaping, advanced typographic composition, automatic font discovery, and text-to-speech are not included.

## Timeline and captions — Milestone C
Scenes are sequenced in manifest order. Each scene's duration defines its global time window; transitions do not shorten or overlap these windows. Layer and caption start/end values are scene-local seconds and use half-open visibility intervals [start, end). The timeline helper maps them to project-global time and provides deterministic frame quantization.

Optional project safe_margins uses normalized fractions (left/right/top/bottom); defaults are 0.05 on every edge. Optional scene captions are timed cues with unique per-scene id, text, normalized x/y/width/height, and font_size. Cues must remain within scene duration and configured safe margins. The module validates and exposes cues; it does not yet render captions or export subtitle files.

## Audio
Tracks reference declared audio assets and require category, timing, gain, and reviewed_non_musical=true. Music, unknown categories, unreviewed audio, embedded audio, and looping are rejected.

## Validate
Run from engine/: `pnata-validate-v3 examples/v03-validation/project.json` and `pytest -q`. Validation does not render; human review remains mandatory.
