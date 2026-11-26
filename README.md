# P'Nata Universal Video Production Studio

**Status:** Universal Skill v0.1.0 + Production Engine v0.1 baseline / v0.2 animated 2D renderer  
**Architecture:** Universal Core + Specialized Production Profiles + capability-aware backends  
**Mode:** Automatic, with escalation for material decisions  
**Delivery target:** MP4 + project/source + assets + QC report when runtime permits

P'Nata covers cinematic, motion graphics, documentary, educational, promotional, social short-form, presentation, and hybrid production. Universal does not mean generic: the shared core governs continuity, rights, policy, timeline, rendering, QC, and handover; specialized profiles define the craft method and quality gates for each format.

## Non-negotiable P'Nata safeguards
1. No music of any kind, without exception.
2. No complete depictions of humans or animals, including silhouettes or figures implied by assembled fragments.
3. No figurative depiction of Allah, prophets, angels, or unseen matters.
4. Permitted audio across the studio: speech/voiceover, genuinely non-musical SFX, genuinely non-musical natural/environmental ambience, or silence.
5. Accuracy, usefulness, rights, and compliance outrank trends or decorative effects.

## Architecture
- `SKILL.md` — master orchestrator.
- `references/` — research, creative direction, visual, assets, audio, render/QC, syariah supervision.
- `profiles/` — specialist production grammar, workflows, and quality gates.
- `docs/` — architecture and quality assurance.
- `engine/` — capability-aware rendering paths, project schemas, policy gates, and technical QC.
- `templates/` — project state and creative brief.
- `tests/` — automated tests and acceptance checklists.

## Specialized profiles
Select one primary profile and normally up to two supporting profiles. Hybrid projects assign profiles by sequence while one primary profile owns editorial coherence.
- [Cinematic](profiles/cinematic.md)
- [Motion Graphics](profiles/motion-graphics.md)
- [Documentary](profiles/documentary.md)
- [Educational](profiles/educational.md)
- [Promotional](profiles/promotional.md)
- [Social Short-form](profiles/social-shortform.md)
- [Presentation](profiles/presentation.md)
- [Hybrid](profiles/hybrid.md)

## Production Engine
- [Engine overview](engine/README.md)
- [v0.2 scene format](engine/SCENE_FORMAT_V0.2.md)
- [v0.2 JSON Schema](engine/schema/scene-project-v0.2.schema.json)

The v0.2 renderer adds deterministic 2D layers, keyframes/easing, and cut/dissolve transitions. It is **not** a universal video editor: each profile must be matched to an actually available backend. See the engine limitations before assigning work.
