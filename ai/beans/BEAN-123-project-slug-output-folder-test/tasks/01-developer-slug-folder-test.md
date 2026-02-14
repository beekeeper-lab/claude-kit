# Task 01: Write Slug Output Folder Test

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-14 15:09 |
| **Completed** | 2026-02-14 15:09 |
| **Duration** | < 1m |

## Goal

Add a test to `tests/test_generator.py` that verifies the generated project subfolder name matches the slug from the CompositionSpec when `output_root` is not explicitly provided.

## Inputs

- `foundry_app/core/models.py` — `ProjectIdentity.resolved_output_folder` property
- `foundry_app/services/generator.py` — `generate_project()` output directory resolution (lines 241-248)
- `tests/test_generator.py` — existing `_make_spec()` helper and `TestEndToEnd` patterns

## Approach

Add a new test class `TestSlugOutputFolder` in `test_generator.py` with a test that:
1. Creates a `_make_spec()` with a specific slug (e.g., "my-cool-project")
2. Sets `output_root` on the spec to a temp directory (not passing `output_root` to `generate_project`)
3. Calls `generate_project()` without the `output_root` parameter so it uses the spec's default path resolution
4. Asserts the output directory basename equals the slug

## Acceptance Criteria

- [ ] Test creates a spec with a known slug
- [ ] Test lets `generate_project` resolve the output path from the spec
- [ ] Test asserts the generated folder name matches the slug
- [ ] Test passes (`uv run pytest tests/test_generator.py -k slug`)

## Definition of Done

Test added, passes, lint clean.
