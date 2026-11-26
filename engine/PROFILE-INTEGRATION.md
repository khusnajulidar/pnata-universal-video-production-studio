# Profile Integration Contract

The Production Engine is an execution layer, not the creative director. It must not assume that every project is a typography slideshow.

## Responsibilities
- Universal Core stores profile selection, scene purpose, timing, assets, layer instructions, audio cues, rights metadata, and QC requirements.
- Creative Director decides visual grammar, story, shot/scene intent, pacing, and quality tier.
- Profiles define specialist craft and acceptance criteria.
- Render adapters execute only the capabilities they support and report unsupported instructions.

## v0.1 boundary
The current renderer supports static typography/still scenes and hard cuts. It is useful for simple title cards, narrated slides, and smoke tests, but is not a cinematic camera system, full motion-graphics compositor, documentary footage editor, or complete presentation authoring tool.

Do not present v0.1 as capable of delivering every profile's highest craft standard. The profile library defines the target method; engine milestones progressively implement backends and scene primitives.
