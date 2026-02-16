# Task 02: Update MCP Writer Tests

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-125-T02 |
| **Owner** | tech-qa |
| **Status** | Pending |
| **Depends On** | T01 |

## Description

Update `tests/test_mcp_writer.py` to verify that Obsidian and Trello MCP servers appear in the generated `mcp.json` output. Ensure existing tests still pass and cover the new baseline servers.

## Acceptance Criteria

- [ ] Test verifies `obsidian` server is present in baseline output
- [ ] Test verifies `trello` server is present in baseline output
- [ ] Test verifies correct command (`uvx` for obsidian, `npx` for trello)
- [ ] Existing tests updated where they assert on exact baseline server count/list
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)
