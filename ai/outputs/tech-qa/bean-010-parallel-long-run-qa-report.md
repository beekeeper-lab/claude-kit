# QA Report: BEAN-010 — Parallel Long Run (tmux)

| Field | Value |
|-------|-------|
| **Bean** | BEAN-010 |
| **Reviewed By** | tech-qa |
| **Date** | 2026-02-07 |
| **Verdict** | GO |

## Acceptance Criteria Trace

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `/long-run --fast N` spawns N tmux child windows | PASS | Command: Parallel Mode section with `tmux new-window` command. Skill: Parallel Phase 3, step 7 with concrete `tmux new-window` syntax. |
| 2 | tmux detection works correctly | PASS | Command: tmux detection subsection checks `$TMUX`, provides user-facing error message. Skill: Parallel Phase 1, step 1 with clear if/else logic. Error table includes `NotInTmux`. |
| 3 | Each child window runs a Claude Code instance with a full team | PASS | Worker spawning command includes `claude --print` with full team wave instructions (BA → Architect → Developer → Tech-QA). |
| 4 | Each child window works on a separate bean on its own feature branch | PASS | Worker instructions include "Create feature branch bean/BEAN-NNN-<slug>" as step 1. Assignment rules: "Never assign the same bean to multiple workers." |
| 5 | Team Lead in main window assigns beans to available workers | PASS | Command: "The main window remains the orchestrator — it does not process beans itself." Skill: Parallel Phase 4, step 11 covers reassignment. |
| 6 | Beans with inter-bean dependencies are not assigned in parallel | PASS | Command: "Only assign beans that have no unmet dependencies on other in-progress or pending beans." Skill: Parallel Phase 3, step 5: "Beans that depend on other pending or in-progress beans are queued, not parallelized." |
| 7 | Progress is reported in the main window as beans complete | PASS | Command: Progress monitoring subsection. Skill: Parallel Phase 4, steps 9-10. |
| 8 | Command/skill format matches existing patterns | PASS | Command follows same markdown structure as sequential mode (sections: Usage, Inputs, Process, Output, Options, Error Handling, Examples). Skill follows phased process pattern with numbered steps. |
| 9 | Team Lead agent updated to reference parallel capability | PASS | `/long-run` row in Skills & Commands table updated to include "Use `--fast N` to run N beans in parallel via tmux child windows." |

## Consistency Check

| Check | Result |
|-------|--------|
| Command ↔ Skill consistency | PASS — Both describe same tmux detection, worker spawning, bean assignment, and monitoring flow |
| Sequential mode unchanged | PASS — All sequential phases (1-6, steps 1-18) untouched in skill; command steps 1-13 unchanged |
| Error tables aligned | PASS — Both command and skill include `NotInTmux` and `WorkerFailure` with matching descriptions |
| Worker spawning command identical | PASS — Same `tmux new-window -n "bean-NNN" "claude --print '...'"` syntax in both files |
| Dependency handling consistent | PASS — Both specify "no unmet dependencies" rule for parallel assignment |

## Issues Found

None.

## Recommendation

**GO** — All 9 acceptance criteria met. Command and skill are consistent with each other and with the existing sequential mode. No contradictions introduced.
