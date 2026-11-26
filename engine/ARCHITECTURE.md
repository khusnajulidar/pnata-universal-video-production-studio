# Production Engine architecture — v0.1 + v0.2

## Execution paths

### v0.1 baseline
Project JSON → loader → policy gates → Pillow still-scene rasterization → FFmpeg H.264 encode → optional reviewed audio mix → FFprobe technical report.

### v0.2 animated 2D
Scene project JSON → strict structural/policy validation → keyframe evaluation → per-layer rasterization → scene transition compositor → FFmpeg H.264 encode → FFprobe technical report.

## v0.2 modules
- `scene_v2.py`: project structure, policy declarations, asset existence/review gates, keyframe bounds and easing validation.
- `render_v2.py`: deterministic 2D layer compositor, transforms, dissolve transitions, frame sequence and FFmpeg encoding.
- `render_v2_cli.py`: command-line entry point.
- `backends.py`: explicit capability declarations and limitations.
- `schema/scene-project-v0.2.schema.json`: machine-readable interchange schema.
- `tests/test_scene_v2.py`: interpolation, easing, clamp, policy and fixture tests.

## v0.2 capability envelope
- Layers: text, rectangle, ellipse, line, reviewed still image.
- Animated numeric properties: x, y, scale, opacity, rotation.
- Easing: linear, ease-in, ease-out, ease-in-out.
- Transitions: cut, dissolve.
- Audio: none in v0.2 renderer.
- Backend: Pillow rasterization + FFmpeg encode.

Unsupported instructions must be rejected or explicitly routed to another verified backend. The capability registry is descriptive; runtime availability still has to be checked before a render.

## Policy boundaries
- Music remains absolutely forbidden.
- Complete depictions of humans/animals, including silhouettes or assembled implied figures, remain absolutely forbidden.
- Each scene requires human visual-policy review; each imported still image requires its own review. This is not automated image understanding and must never be presented as a machine certification.
- v0.2 is silent-only. Do not bypass this by embedding audio in a video/image asset or by treating music as ambience.

## Known limitations
No 3D scene graph, camera/lens simulation, lighting engine, advanced vector path animation, particle simulation, masks, footage editing, audio mixing, subtitle engine, semantic music detector, or automatic rights verification. Dissolve is a simple blend from the previous scene's final rendered frame. Human review and creative/factual review remain external quality gates.
