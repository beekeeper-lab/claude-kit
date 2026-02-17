# BEAN-140: Trello-Bean Lifecycle Mapping

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-140 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-16 |
| **Started** | 2026-02-16 |
| **Completed** | 2026-02-16 19:15 |
| **Duration** | < 1m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The Foundry AI team uses Trello as an external work-intake and status-tracking tool, but the full lifecycle mapping between Trello cards and the bean system is undocumented. `/trello-load` creates beans from Trello cards (inbound) and `/long-run` + `/merge-bean` move Trello cards to Completed (outbound). Understanding this bidirectional flow — its touchpoints, data transformations, failure modes, and gaps — is essential for improving the integration and preventing data drift between the two systems.

## Goal

Produce a comprehensive analysis document that maps the complete Trello-Bean lifecycle: how cards become beans, how bean state changes propagate back to Trello, what data is preserved/lost at each transition, and where the integration has gaps or risks.

## Scope

### In Scope
- Full lifecycle mapping: Trello card → Bean creation → Bean execution → Trello card completion
- Data transformation analysis at each transition point
- State machine diagram showing all Trello list ↔ Bean status correspondences
- Gap analysis: where state can diverge between systems
- Failure mode inventory for each integration point
- Cross-referencing BEAN-132 (long-run analysis) and BEAN-136 (trello-load analysis)

### Out of Scope
- Implementation of improvements (future beans)
- Trello MCP server internals
- Non-Trello intake paths (e.g., /backlog-refinement)

## Acceptance Criteria

- [x] Analysis document covers the complete inbound flow (Trello → Bean)
- [x] Analysis document covers the complete outbound flow (Bean → Trello)
- [x] State mapping table shows all Trello list ↔ Bean status correspondences
- [x] Data transformation analysis identifies what is preserved/lost at each transition
- [x] Failure modes are inventoried for each integration point
- [x] Gap analysis identifies where systems can diverge
- [x] Document references BEAN-132 and BEAN-136 findings
- [x] Output file is in ai/outputs/team-lead/

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Analyze Trello-Bean lifecycle and produce mapping document | Developer | — | Done |

> BA and Architect skipped — this is a Process analysis bean with no requirements ambiguity or architectural decisions. The scope is well-defined by prior analyses (BEAN-132, BEAN-136).
> Tech QA skipped — this is a Process analysis bean that modifies no code. The output is a documentation artifact, not executable code.

## Notes

- References BEAN-132 (long-run analysis) and BEAN-136 (trello-load analysis) which have been completed
- This bean synthesizes findings from both prior analyses into a unified lifecycle mapping
- BA/Architect skip reason: Process analysis bean — scope fully defined by prior analyses, no requirements gathering or architectural decisions needed
- Tech QA skip reason: Process bean producing only a documentation artifact — no code changes, no tests to verify

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Analyze Trello-Bean lifecycle | Developer | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
