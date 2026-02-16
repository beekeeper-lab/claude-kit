# BEAN-130: Telemetry Cost Estimation

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-130 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-16 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The telemetry system tracks token usage (input and output) per task and per bean, but there's no way to see the actual dollar cost of running beans. Token counts alone don't convey cost because input and output tokens have different rates, and those rates change over time as Anthropic updates pricing. Without cost visibility, it's hard to budget, identify expensive patterns, or compare the cost-effectiveness of different approaches.

## Goal

Every telemetry table (in bean.md files and in `/telemetry-report` output) shows a `Cost` column computed from token counts and configurable per-token rates. Rates are stored in a single config file that's easy to update when pricing changes.

## Scope

### In Scope
- Create a token pricing config file at `ai/context/token-pricing.md` with input and output cost-per-token rates
- Update the bean telemetry template (`ai/beans/_bean-template.md`) to include a `Cost` column in the per-task table and a `Total Cost` row in the summary table
- Update the `/telemetry-report` skill (`.claude/skills/telemetry-report/SKILL.md`) to:
  - Read rates from the config file
  - Compute cost per task: `(tokens_in * input_rate) + (tokens_out * output_rate)`
  - Show cost per task, per bean, and in aggregate summaries
  - Add cost columns to category and owner breakdown tables
- Update telemetry-writing skills/hooks (e.g., `/close-loop`, telemetry-stamp) to compute and write the Cost column when recording task telemetry in bean.md

### Out of Scope
- Historical backfill of cost data into existing bean.md files (can be a follow-up bean)
- Multiple model pricing tiers (use a single rate pair for the primary model)
- Currency conversion or localization
- Cost alerts or budgeting features

## Acceptance Criteria

- [ ] `ai/context/token-pricing.md` exists with clearly labeled input and output rates ($/token)
- [ ] Rates in the config file use current Anthropic pricing for the primary model used (Claude Opus 4)
- [ ] Bean template telemetry table has a `Cost` column
- [ ] Bean template summary table has a `Total Cost` row
- [ ] `/telemetry-report` reads rates from the config file (not hardcoded)
- [ ] `/telemetry-report` single-bean view shows cost per task and total cost
- [ ] `/telemetry-report` aggregate view shows cost in category and owner breakdowns
- [ ] Telemetry-writing automation computes and writes the Cost field when recording task data
- [ ] Changing rates in the config file changes the computed costs in `/telemetry-report` output
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Suggested config format for `ai/context/token-pricing.md`:
  ```
  # Token Pricing

  | Field | Value |
  |-------|-------|
  | **Model** | Claude Opus 4 |
  | **Input Rate** | $0.000015 per token ($15/MTok) |
  | **Output Rate** | $0.000075 per token ($75/MTok) |
  | **Updated** | 2026-02-16 |
  ```
- Cost formula: `cost = (tokens_in * input_rate) + (tokens_out * output_rate)`
- Display format: `$0.42` (two decimal places for most values, `< $0.01` for very small amounts)
- The config file approach means updating pricing requires editing one file, not multiple skills
- Consider showing cost in the bean metadata table too (next to Duration) for quick reference

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
