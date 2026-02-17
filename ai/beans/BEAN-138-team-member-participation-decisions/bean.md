# BEAN-138: Team Member Participation Decisions

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-138 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-16 |
| **Started** | 2026-02-16 |
| **Completed** | 2026-02-16 19:11 |
| **Duration** | < 1m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The AI team workflow defines a natural wave (BA → Architect → Developer → Tech-QA) for task decomposition, but the guidance for when to skip personas is vague: "skip roles not needed." There is no centralized decision framework that specifies which team members should participate based on bean category (App/Process/Infra), bean type (feature, bug fix, refactor, analysis, etc.), or complexity. This leads to inconsistent decomposition decisions and occasional inclusion of personas who add no value to a given bean, or omission of personas whose input would improve quality.

## Goal

Produce an analysis document that defines clear participation rules for each team persona across different bean categories and types. The document should serve as a reference for Team Lead decomposition decisions, reducing ambiguity and improving consistency.

## Scope

### In Scope
- Analyze historical bean decomposition patterns across all completed beans
- Document which personas participated (and were skipped) for each bean category
- Identify patterns where skipping a persona caused issues or where including one added no value
- Define a participation decision matrix by bean category and type
- Provide skip justification templates for common scenarios
- Document exceptions and override conditions

### Out of Scope
- Modifying agent definition files
- Modifying the bean workflow documentation
- Implementing any recommended changes to skills or commands
- Changing the decomposition logic in any skill

## Acceptance Criteria

- [x] Analysis document exists at `ai/outputs/team-lead/bean-138-team-member-participation-decisions.md`
- [x] Document includes a participation decision matrix covering all bean categories (App/Process/Infra) and common types
- [x] Document analyzes historical patterns from completed beans
- [x] Document provides skip justification templates
- [x] Document defines override/exception conditions
- [x] No code changes required (Process analysis bean)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Analyze beans and write participation decisions document | developer | — | Done |
| 2 | Review analysis document against acceptance criteria | team-lead | 1 | Done |

> BA/Architect skipped: Process analysis bean — no requirements gathering or architecture design needed; the task is analysis of existing workflow patterns and documentation.
> Tech QA skipped: No code changes to test — output is a documentation artifact only.

## Notes

Part of a batch of Process analysis beans (BEAN-137 through BEAN-139) analyzing team member assignment and participation patterns. BEAN-137 covers assignment analysis, BEAN-138 covers participation decisions, BEAN-139 covers recommendations.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Analyze beans and write document | developer | — | — | — | — |
| 2 | Verify criteria | team-lead | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
