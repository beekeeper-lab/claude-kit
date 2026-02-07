# Task 01: Enforce Branching in All Workflow Docs and Skills

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Update all workflow docs, skills, and agent files to make feature branching mandatory (not optional) for every bean.

## Inputs

- `ai/beans/BEAN-012-enforce-branch-workflow/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — workflow to update
- `.claude/skills/pick-bean/SKILL.md` — skill to update
- `.claude/skills/long-run/SKILL.md` — already references branching, verify enforcement
- `.claude/agents/team-lead.md` — agent to update
- `.claude/agents/developer.md` — agent to update

## Implementation

1. **`ai/context/bean-workflow.md`**: Update Branch Strategy section to make branching mandatory. Remove any language suggesting it's optional. State: "Every bean MUST have its own feature branch."
2. **`.claude/skills/pick-bean/SKILL.md`**: Make branch creation the default (not opt-in). Remove `--no-branch` or make it require explicit justification. Add step: "Check for `test` branch; create from `main` if missing."
3. **`.claude/skills/long-run/SKILL.md`**: Verify Phase 3 step 8 enforces branch creation. Add note that skipping branches is not allowed.
4. **`.claude/agents/team-lead.md`**: Add rule: "Always create a feature branch when picking a bean. Never commit directly to `main`."
5. **`.claude/agents/developer.md`**: Add rule: "All work happens on the feature branch. Never commit to `main`."
6. **`.claude/commands/pick-bean.md`**: Update to reflect mandatory branching.

## Acceptance Criteria

- [ ] `bean-workflow.md` makes branching mandatory
- [ ] `/pick-bean` skill enforces branch creation by default
- [ ] `/long-run` skill verified to enforce branching
- [ ] Team Lead agent has branch-first rule
- [ ] Developer agent has branch-first rule
- [ ] `test` branch creation documented (check + create if missing)
- [ ] All docs standardize on `test` as the integration branch name

## Definition of Done

All workflow docs and skills enforce branching. No optional branching language remains.
