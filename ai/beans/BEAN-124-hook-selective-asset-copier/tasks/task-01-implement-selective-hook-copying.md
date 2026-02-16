# Task 01: Implement Selective Hook Copying

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-124-T01 |
| **Bean** | BEAN-124 |
| **Owner** | developer |
| **Status** | Pending |
| **Depends On** | — |

## Description

Modify `foundry_app/services/asset_copier.py` to filter hook files based on the user's hook pack selections in `spec.hooks.packs`. Currently, all hook files from the library are copied wholesale. After this change, only hooks whose pack IDs appear in `spec.hooks.packs` with `enabled=True` are copied.

## Implementation Plan

1. Remove `("claude/hooks", ".claude/hooks")` from `_GLOBAL_ASSET_DIRS` (it should no longer be copied wholesale)
2. Add a new function `_copy_selected_hooks()` that:
   - Builds a set of enabled hook pack IDs from `spec.hooks.packs`
   - If the set is empty, skips hook copying entirely
   - Iterates files in `library_root/claude/hooks/`
   - Only copies files whose stem (filename without extension) matches an enabled pack ID
   - Uses the same overlay-safe copy logic as `_copy_directory_files`
3. Call `_copy_selected_hooks()` from `copy_assets()` after the global asset loop

## Acceptance Criteria

- [ ] Hook files are only copied when their pack ID is in `spec.hooks.packs` with `enabled=True`
- [ ] If no packs are selected (empty list or all disabled), no hooks are copied
- [ ] Commands and skills continue to be copied in full
- [ ] Settings, beans, and context dirs continue to be copied in full
- [ ] Overlay-safe behavior preserved for hook copying

## Files to Modify

- `foundry_app/services/asset_copier.py`
