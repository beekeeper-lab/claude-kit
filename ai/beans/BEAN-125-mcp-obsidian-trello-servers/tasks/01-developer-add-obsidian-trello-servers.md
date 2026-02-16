# Task 01: Add Obsidian & Trello MCP Server Definitions

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-125-T01 |
| **Owner** | developer |
| **Status** | Pending |
| **Depends On** | — |

## Description

Add Obsidian and Trello MCP server entries to `foundry_app/services/mcp_writer.py`. These should be added to `_BASELINE_SERVERS` (always included) since they are common project management tools.

### Obsidian MCP Server
- Package: `mcp-obsidian` (Python, runs via `uvx`)
- Command: `uvx`
- Args: `["mcp-obsidian"]`

### Trello MCP Server
- Package: `@delorenj/mcp-server-trello` (npm, runs via `npx`)
- Command: `npx`
- Args: `["-y", "@delorenj/mcp-server-trello"]`

## Acceptance Criteria

- [ ] `_BASELINE_SERVERS` includes `obsidian` entry with `uvx` command
- [ ] `_BASELINE_SERVERS` includes `trello` entry with `npx` command
- [ ] Existing filesystem and stack-specific servers unchanged
