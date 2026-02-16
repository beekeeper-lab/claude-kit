# Task 02: Update Tests for Selective Hook Copying

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-124-T02 |
| **Bean** | BEAN-124 |
| **Owner** | tech-qa |
| **Status** | Pending |
| **Depends On** | T01 |

## Description

Update `tests/test_asset_copier.py` to cover the new selective hook copying behavior. Existing hook tests assume all hooks are always copied — these need updating. Add new tests for various pack selection scenarios.

## Implementation Plan

1. Update `_make_spec()` helper to accept `hooks` parameter (or add a helper for creating HooksConfig)
2. Update existing `TestHookCopying` tests to pass explicit hook pack selections
3. Add new tests:
   - Hook files copied only when matching packs are enabled
   - No hooks copied when no packs selected (empty list)
   - No hooks copied when packs present but all disabled
   - Only matching hooks copied with partial selection
   - Commands and skills still copied in full regardless of hook selections
   - Overlay behavior works correctly with selective hooks
4. Update `TestStageResult.test_wrote_count_matches_expected` to account for selective hook behavior
5. Update `TestEdgeCases.test_empty_persona_list` which currently asserts hooks are always copied

## Acceptance Criteria

- [ ] All existing tests updated for selective behavior
- [ ] New tests cover: full selection, partial selection, empty selection, disabled packs
- [ ] Tests verify commands/skills are unaffected by hook filtering
- [ ] All tests pass (`uv run pytest`)

## Files to Modify

- `tests/test_asset_copier.py`
