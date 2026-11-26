# Scene Project Format v0.3 — Milestone A

This manifest is validated metadata only. It does not mean v0.3 rendering, layout, or audio mixing is implemented.

## Project
Required: `version: "0.3"`, title, canvas width/height, fps, duration, policy, assets, scenes. Optional audio_tracks defaults to empty.

## Hard policy
Required fixed values: music, complete_living_beings, unseen_depictions = `forbidden`.

## Assets
Each asset has a unique id, project-relative path, media_type, source, rights_status=`cleared`, and policy_reviewed=true. Files must exist under the project directory; path traversal is rejected. Audio assets must declare narration, sfx, or natural_ambience. Visual assets with embedded audio are rejected. These are human workflow attestations, not automated rights or semantic certification.

## Scenes and layers
Scenes have unique IDs, positive duration, visual_reviewed_policy_compliant=true, and layers. Layer times are seconds relative to the scene. Text requires text, box dimensions, and font size. Images reference declared image assets and choose contain/cover/stretch. Keyframes are limited to x/y/scale/opacity/rotation.

## Audio
Tracks reference declared audio assets and require category, timing, gain, and reviewed_non_musical=true. Music, unknown categories, unreviewed audio, embedded audio, and looping are rejected.

## Validate
Run from engine/: `pnata-validate-v3 examples/v03-validation/project.json` and `pytest -q`. Validation does not render; human review remains mandatory.
