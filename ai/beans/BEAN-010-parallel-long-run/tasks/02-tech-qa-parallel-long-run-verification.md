# Task 02: Parallel Long Run Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify the parallel long run updates are complete, consistent, and well-documented.

## Inputs

- `ai/beans/BEAN-010-parallel-long-run/bean.md` — acceptance criteria
- `.claude/commands/long-run.md` — updated command
- `.claude/skills/long-run/SKILL.md` — updated skill
- `.claude/agents/team-lead.md` — updated agent

## Acceptance Criteria

- [ ] All bean acceptance criteria traced and met
- [ ] tmux detection is clearly specified
- [ ] Worker spawning commands are concrete and correct
- [ ] Dependency handling prevents parallel execution of dependent beans
- [ ] No contradictions with sequential `/long-run` mode
- [ ] QA report written to `ai/outputs/tech-qa/bean-010-parallel-long-run-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
