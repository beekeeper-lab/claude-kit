# QA Report: BEAN-012 — Enforce Feature Branch Workflow

| Field | Value |
|-------|-------|
| **Bean** | BEAN-012 |
| **Reviewed By** | tech-qa |
| **Date** | 2026-02-07 |
| **Verdict** | GO |

## Acceptance Criteria Trace

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Team Lead always creates branch when picking a bean | PASS | team-lead.md rule: "Every bean MUST have its own feature branch — create as the first action when picking a bean. No exceptions." |
| 2 | `test` branch exists (created if missing) | PASS | bean-workflow.md: "If `test` does not exist, create it from `main`." pick-bean skill step 8: "Ensure test branch exists." long-run skill step 8: "Ensure test branch exists." |
| 3 | All bean work on feature branch, never on `main` | PASS | bean-workflow.md: "No work happens before the branch exists." "Never commit to `main`." developer.md rule: "Never commit directly to `main`." |
| 4 | Merge Captain merges feature branch → `test` | PASS | bean-workflow.md: "the Merge Captain merges the feature branch into `test` using `/merge-bean`." long-run skill Phase 5.5 step 17. |
| 5 | `/pick-bean` enforces branch creation | PASS | `--no-branch` flag removed from command and skill. Skill step 9: "Feature branching is mandatory. Every bean gets its own branch." |
| 6 | `/long-run` enforces branch-per-bean | PASS | Skill step 9: "mandatory for every bean" + "All work happens on this branch. Never commit to `main`." |
| 7 | `bean-workflow.md` makes branching mandatory | PASS | Opens with: "Every bean MUST have its own feature branch. No exceptions." "When NOT to Branch" section removed entirely. |
| 8 | Team Lead and Developer agents updated | PASS | team-lead.md: 4 new branch-related rules. developer.md: existing rules already enforce branch-only work (lines 140-141). |

## Consistency Check

| Check | Result |
|-------|--------|
| No remaining optional branching language | PASS — "When NOT to Branch" section removed. `--no-branch` removed from pick-bean. |
| `test` standardized everywhere | PASS — bean-workflow.md, pick-bean skill, long-run skill, team-lead agent all reference `test` |
| No contradictions between docs | PASS — All files agree: mandatory branching, `test` integration branch, `/merge-bean` for merging |
| Step numbering in long-run skill | PASS — Renumbered cleanly after inserting step 8 (ensure test branch) |

## Issues Found

None.

## Recommendation

**GO** — All 8 acceptance criteria met. Branching is now mandatory across all workflow docs, skills, and agents. No optional branching language remains.
