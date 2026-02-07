# Task 02: Design Spec for Overlay Engine

| Field | Value |
|-------|-------|
| **Owner** | architect |
| **Depends On** | 01 |
| **Status** | Done |

## Goal

Produce a design specification that defines how the overlay engine integrates with the existing generator pipeline. The Developer should be able to implement from this spec without architectural guesswork.

## Inputs

- `ai/outputs/ba/bean-002-overlay-requirements.md` — requirements from BA
- `ai/beans/BEAN-002-generator-overlay/bean.md` — bean context
- `foundry_app/services/generator.py` — current pipeline orchestrator
- `foundry_app/services/scaffold.py` — current scaffold (creates fresh structure)
- `foundry_app/services/safety.py` — writes settings.local.json
- `foundry_app/core/models.py` — StageResult, GenerationManifest, CompositionSpec
- `foundry_app/cli.py` — current CLI interface
- `ai/context/project.md` — architecture overview

## Deliverables

Write to `ai/outputs/architect/bean-002-overlay-design.md`:

1. **Component design** — where does overlay logic live?
   - New module vs. extending generator.py vs. a wrapper
   - How overlay interacts with each pipeline stage (scaffold, compile, copy_assets, seed)
   - Which stages need overlay-awareness and which work unchanged

2. **Conflict detection strategy:**
   - How to determine if a file is "Foundry-managed" vs. "user-managed"
   - Using the manifest (`ai/generated/manifest.json`) to track what Foundry wrote last time
   - Conflict report data structure (file path, reason, existing hash, generated hash)

3. **Dry-run design:**
   - How dry-run mode short-circuits actual writes
   - Output format for dry-run report (what would be created, updated, skipped, conflicted)

4. **CLI interface design:**
   - New args: `--overlay`, `--dry-run`
   - How `--overlay` changes the output path behavior
   - Error cases (overlay on non-existent dir, overlay without --overlay flag on existing dir)

5. **API changes:**
   - `generate_project()` signature changes (new `overlay: bool`, `dry_run: bool` params?)
   - New return types or fields on `GenerationManifest`
   - Impact on `StageResult` (needs "skipped" or "conflict" tracking?)

6. **ADR** — record the key decision: overlay as a mode of the existing pipeline (not a separate tool)

## Acceptance Criteria

- [ ] Design covers all pipeline stages and how each behaves in overlay mode
- [ ] Conflict detection strategy is concrete (not hand-wavy)
- [ ] Dry-run output format is specified
- [ ] CLI interface is specified with examples
- [ ] API changes are listed with before/after signatures
- [ ] ADR is written and appended to `ai/context/decisions.md`
- [ ] Design is implementable by the Developer within the existing codebase patterns

## Definition of Done

- [ ] `ai/outputs/architect/bean-002-overlay-design.md` exists with all deliverables
- [ ] ADR appended to `ai/context/decisions.md`
- [ ] Design reviewed: no ambiguity in component boundaries or data flow
