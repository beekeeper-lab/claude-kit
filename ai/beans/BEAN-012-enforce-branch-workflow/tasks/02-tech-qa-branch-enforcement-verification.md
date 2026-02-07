# Task 02: Branch Enforcement Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify the branch enforcement is complete and consistent across all docs.

## Inputs

- `ai/beans/BEAN-012-enforce-branch-workflow/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — updated workflow
- `.claude/skills/pick-bean/SKILL.md` — updated skill
- `.claude/skills/long-run/SKILL.md` — verified skill
- `.claude/agents/team-lead.md` — updated agent
- `.claude/agents/developer.md` — updated agent

## Acceptance Criteria

- [ ] All bean acceptance criteria traced and met
- [ ] No remaining optional branching language
- [ ] `test` branch standardized everywhere
- [ ] No contradictions between docs
- [ ] QA report written to `ai/outputs/tech-qa/bean-012-enforce-branch-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
