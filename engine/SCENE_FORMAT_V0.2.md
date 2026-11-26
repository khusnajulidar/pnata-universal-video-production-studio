# Scene Project Format v0.2

This format describes a timed 2D composition. It is explicit at project level; the current Pillow/FFmpeg backend implements only the capabilities listed in engine/README.md.

## Project
Required: `title`, `width`, `height`, `fps`, `duration`, `scenes`, and `policy`.
- Canvas dimensions are pixels.
- `fps` is an integer from 1 to 120.
- Scene durations are seconds and must cover the declared project duration.
- Policy must explicitly forbid music and complete depictions of living beings.
- v0.2 renderer accepts no audio tracks.

## Scene
A scene has `duration`, `visual_reviewed_policy_compliant: true`, optional `background`, optional `transition_in`, and `layers`.
Transitions: `{"type":"cut"}` or `{"type":"dissolve","duration":0.6}`.

The visual-review flag is a human workflow declaration, not proof of compliance. Review rendered frames and confirm no complete human/animal figure or implied figure appears.

## Layers
- `text`: text string, font size, color.
- `rect`: rectangle with optional rounded corners.
- `ellipse`: ellipse.
- `line`: horizontal line primitive.
- `image`: still image with path and `asset_reviewed_policy_compliant: true`.

Position `x` and `y` are normalized canvas coordinates. Width/height for geometric and text layers are normalized canvas fractions. Image width/height are pixels. Scale is multiplicative; opacity is 0–1; rotation is degrees.

## Keyframes
Animate numeric properties `x`, `y`, `scale`, `opacity`, and `rotation`. Times are seconds from scene start. Supported easing: `linear`, `ease_in`, `ease_out`, `ease_in_out`.

```json
{"keyframes":{"x":[{"time":0,"value":0.2,"ease":"ease_out"},{"time":1.5,"value":0.8}],"opacity":[{"time":0,"value":0},{"time":0.4,"value":1}]}}
```

## Example
Run from `engine/`:
```bash
pnata-render-v2 examples/v02-motion/project.json -o dist/v02.mp4 --qc dist/v02-qc.json
```

## Validation limits
The loader validates structure, policy declarations, asset existence, review declarations, keyframe properties/easing, and timeline coverage. It does not infer whether visuals depict a living being, verify factual claims, clear copyright, or certify artistic quality.
