# QA Report: BEAN-013 — Deploy Command

| Field | Value |
|-------|-------|
| **Bean** | BEAN-013 |
| **Reviewed By** | tech-qa |
| **Date** | 2026-02-07 |
| **Verdict** | GO |

## Acceptance Criteria Trace

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `/deploy` command and skill created | PASS | `deploy.md` command (91 lines), `deploy/SKILL.md` skill (149 lines) |
| 2 | Tests run against `test` branch | PASS | Command step 3, Skill Phase 2 step 5: `uv run pytest` |
| 3 | Code quality review by code-quality-reviewer | PASS | Skill Phase 2 step 6: reviews `git diff main..test`, writes report to `ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md` |
| 4 | Security review by security-engineer | PASS | Skill Phase 2 step 7: reviews diff for OWASP top 10, writes report to `ai/outputs/security-engineer/deploy-YYYY-MM-DD.md` |
| 5 | Release notes listing all beans since last deploy | PASS | Skill Phase 3 steps 9-11: parses `git log main..test`, cross-references `_index.md`, generates per-bean summaries |
| 6 | User presented with summary, asked for approval | PASS | Skill Phase 4 step 12: formatted summary block with beans, reviews, tests. Step 13: "User must explicitly say 'go'" |
| 7 | Merge only after user says "go" | PASS | Skill step 13: "If 'abort' or anything else: report 'Deploy aborted by user'". Phase 5 only reached after "go". |
| 8 | Safe merge: test → main with --no-ff, push | PASS | Skill step 16: `git merge test --no-ff`, step 18: `git push origin main` |
| 9 | Command/skill format matches existing patterns | PASS | Same section structure as merge-bean (Inputs, Process, Outputs, Error Handling, Examples). Skill uses phased process. |
| 10 | Team Lead agent updated | PASS | `/deploy` row added to Skills & Commands table: "The only authorized path to `main`." |

## Consistency Check

| Check | Result |
|-------|--------|
| Command ↔ Skill consistency | PASS — Both describe same 5-phase process |
| Consistent with branch workflow | PASS — Complements BEAN-012: beans → test (via merge-bean), test → main (via deploy) |
| Review output paths consistent | PASS — Both command and skill use `ai/outputs/<persona>/deploy-YYYY-MM-DD.md` |
| Error tables aligned | PASS — Both include same 6 error types |
| No auto-merge to main | PASS — Always requires user "go" |

## Issues Found

None.

## Recommendation

**GO** — All 10 acceptance criteria met. The deploy command provides a complete quality gate (tests + 2 reviews + user approval) before any code reaches `main`.
