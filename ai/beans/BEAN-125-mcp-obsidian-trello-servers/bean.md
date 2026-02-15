# BEAN-125: MCP Config — Obsidian & Trello Servers

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-125 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-15 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The MCP config writer (`mcp_writer.py`) generates `.claude/mcp.json` with a filesystem baseline and stack-specific doc servers (python, node, react, typescript). It does not include Obsidian or Trello MCP servers, which are commonly used tools for project management and documentation review. Users should get these servers pre-configured so they can use them immediately without manual setup.

## Goal

Generated projects include Obsidian and Trello MCP server entries in `.claude/mcp.json` alongside the existing baseline and stack-specific servers. Users can remove what they don't need, but the common tooling is there by default.

## Scope

### In Scope
- Add Obsidian MCP server definition to `_BASELINE_SERVERS` or a new `_TOOL_SERVERS` mapping in `mcp_writer.py`
- Add Trello MCP server definition similarly
- Research correct MCP package names and configuration for both servers
- Update tests to verify the new servers appear in generated output

### Out of Scope
- Making MCP server selection configurable in the wizard (users can edit mcp.json after generation)
- Adding MCP servers for every possible tool
- Configuring MCP for the Foundry project itself

## Acceptance Criteria

- [ ] Generated `mcp.json` includes an Obsidian MCP server entry with correct package and args
- [ ] Generated `mcp.json` includes a Trello MCP server entry with correct package and args
- [ ] Existing filesystem and stack-specific servers are unchanged
- [ ] MCP writer tests updated to verify new server entries
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Need to verify the correct npm package names for Obsidian and Trello MCP servers
- These should be added to the baseline (always included) rather than conditional on stack selection
- Related to BEAN-070 (MCP Config Generation) which created the original MCP writer

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
