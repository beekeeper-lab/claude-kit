# Task 01: Analyze Long Run Skill

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-16 |
| **Completed** | 2026-02-16 |

## Goal

Perform a comprehensive analysis of the `/long-run` command skill file (`.claude/skills/long-run/SKILL.md`) and produce a structured analysis document.

## Inputs

- `.claude/skills/long-run/SKILL.md` — primary analysis target
- `.claude/skills/merge-bean/SKILL.md` — dependency: merge captain
- `.claude/skills/deploy/SKILL.md` — dependency: deployment
- `.claude/skills/pick-bean/SKILL.md` — dependency: bean selection
- `.claude/commands/spawn-bean.md` — dependency: parallel worker spawning
- `ai/context/bean-workflow.md` — dependency: lifecycle reference

## Definition of Done

- [ ] Analysis document written to `ai/outputs/team-lead/bean-132-long-run-analysis.md`
- [ ] All sequential phases covered (Phase 0 through Phase 6)
- [ ] Parallel mode covered
- [ ] Dependencies mapped
- [ ] Strengths and weaknesses identified
- [ ] Improvement recommendations provided
