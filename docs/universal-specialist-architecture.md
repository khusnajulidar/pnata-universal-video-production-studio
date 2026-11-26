# Universal Core + Specialized Production Profiles

## Design decision
Universal coverage does not mean generic execution. P'Nata uses one shared production core and a library of deep specialist profiles. The core owns governance, continuity, project data, asset tracking, render orchestration, QC, and delivery. Profiles own the craft grammar and quality standards for each video type.

## Four layers
1. Universal Core: brief, project state, policies, sources/rights, timeline, asset manifest, capability detection, render orchestration, QC, packaging.
2. Creative Director: interprets the brief, selects primary/supporting profiles, sets quality target, resolves trade-offs, protects message.
3. Specialist Profiles: cinematic, motion graphics, documentary, educational, promotional, social short-form, presentation, hybrid.
4. Execution Adapters: actual tools available in a runtime. Profiles define required quality; adapters define what can be executed.

## Consequences and controls
- Breadth requires more specialist knowledge to maintain. Profiles are versioned and independently tested.
- One renderer cannot serve every style equally. Select rendering backends per project/scene; never force all work through the simplest backend.
- Hybrid projects need orchestration. One primary profile owns coherence.
- Higher quality requires planning and review. Allocate resources to story, assets, edit iterations, and QC according to risk and ambition.
- Tool availability varies. Disclose gaps and propose a viable fallback without pretending equivalence.
- Breadth must not become shallow checklists. A profile is not production-ready until workflow, failure modes, and acceptance tests exist.

## Profile selection protocol
Extract goal, audience, platform, message, action, factual/religious risk, assets, and delivery constraints. Determine the audience outcome and storytelling vehicle. Select one primary profile and normally up to two supporting profiles. Assign scenes to profiles when needed. Record rationale and quality gates. Re-evaluate if the brief changes materially.

## Quality target
Evaluate three independent axes:
- Substance: accuracy, clarity, narrative integrity, usefulness, evidence, ethical treatment.
- Craft: composition, design, motion, cinematography, editing, sound intelligibility, pacing.
- Delivery: technical integrity, accessibility, rights, policy compliance, reproducibility, handover.

Mandatory gates must pass on all axes. Technical polish cannot compensate for factual, syariah, rights, or policy failure.

## Quality tiers
- Baseline: complete, clear, technically sound, policy-compliant.
- Polished: refined story, coherent art direction, custom asset treatment, careful pacing, full editorial and technical QC.
- Signature: distinctive creative concept, tailored visual grammar, intentional shot/scene design, multiple review passes, detailed finishing, documented rationale.

Target the highest tier compatible with the brief, tools, rights, and schedule. Never silently downgrade. Explain any limiting factor and propose staged delivery.

## Non-negotiable P'Nata gates
No music of any kind. Allowed audio: speech/voiceover, genuinely non-musical SFX, genuinely non-musical natural/environmental ambience, or silence. No beat-like SFX patterns.
No complete depictions of humans or animals, including silhouettes; do not assemble fragments into a complete implied figure. No figurative depiction of Allah, prophets, angels, or unseen matters.
Require source/rights verification, factual integrity, religious review where applicable, accessibility/readability, technical QC, and truthful status reporting.

## Engine implications
Do not add one monolithic style switch to the renderer. Represent scenes as structured units with profile tags, layers, timing, assets, text, motion instructions, audio cues, and QC metadata. Backend selection belongs to execution adapters. Profiles are declarative and testable, not hard-coded into one visual template.
