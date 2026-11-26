# P'Nata Universal Video Production Studio

**Status:** Universal Skill v0.1.0 + Production Engine v0.1.0 starter  
**Architecture:** Universal Core + Specialized Production Profiles  
**Mode:** Automatic, with escalation for material decisions  
**Delivery target:** MP4 + project/source + assets + QC report when runtime permits

P'Nata covers cinematic, motion graphics, documentary, educational, promotional, social short-form, presentation, and hybrid production. Universal does not mean generic: the shared core governs continuity, rights, policy, timeline, rendering, QC, and handover; specialized profiles define the craft method and quality gates for each format.

## Non-negotiable P'Nata safeguards
1. No music of any kind, without exception.
2. No complete depictions of humans or animals, including silhouettes or figures implied by assembled fragments.
3. No figurative depiction of Allah, prophets, angels, or unseen matters.
4. Permitted audio: speech/voiceover, genuinely non-musical SFX, genuinely non-musical natural/environmental ambience, or silence.
5. Accuracy, usefulness, rights, and compliance outrank trends or decorative effects.

## Architecture
- `SKILL.md` — master orchestrator.
- `references/` — research, creative direction, visual, assets, audio, render/QC, syariah supervision.
- `profiles/` — specialist production grammar, workflows, and quality gates.
- `docs/universal-specialist-architecture.md` — architecture and trade-offs.
- `docs/quality-assurance-framework.md` — substance, craft, and delivery QA.
- `engine/` — Python + FFmpeg starter renderer, project schema, capability checker, policy gates, and FFprobe QC.
- `templates/` — project state and creative brief.
- `tests/` — acceptance checklists.

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
See [engine/README.md](engine/README.md). v0.1 can render typography/still scenes with hard cuts to H.264 MP4 and create a technical FFprobe report. It is a starter backend, not a full cinematic editor, advanced motion compositor, or universal renderer. Unsupported instructions must be reported, never silently ignored.

## Quality target
- **Baseline:** complete, clear, technically sound, compliant.
- **Polished:** refined story, coherent art direction, custom asset treatment, careful pacing, full editorial and technical QC.
- **Signature:** distinctive creative concept, tailored visual grammar, intentional shot/scene design, multiple review passes, detailed finishing.

Aim for the highest tier justified by the brief, rights, runtime, and available tools. Never silently downgrade quality.

## Use
Give the studio a brief, or ask it to continue an existing project. It must audit approved decisions and assets, choose the specialist profile(s), research and plan, execute with available backends, inspect the full result, and deliver a truthful QC report.
