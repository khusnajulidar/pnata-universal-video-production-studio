# Engine architecture v0.1.0

Data flow: project JSON → structural loader → policy gates → Pillow scene rasterization → FFmpeg H.264 encode → optional reviewed audio mix → FFprobe report.

- `project.py`: project loading and baseline validation.
- `policy.py`: hard audio-role gates, human audio review declaration, project policy flags, and image-review gate.
- `render.py`: typography-first still scenes and hard-cut MP4 assembly.
- `qc.py`: file/container/stream metadata; no semantic approval claims.
- `capabilities.py`: conservative runtime inventory.

v0.1 does not implement keyframed animation, transitions, subtitles, nested compositions, multitrack visual compositing, semantic music detection, or automated certification of visual compliance. Those are later milestones, not assumed capabilities.
