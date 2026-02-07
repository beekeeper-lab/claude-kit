# BEAN-005: Compiled Prompt Project Context — QA Report

**Author:** Tech-QA | **Date:** 2026-02-07 | **Bean:** BEAN-005

## Verdict: GO

## Test Results

- **Total tests:** 323 (313 existing + 10 new)
- **Pass:** 323
- **Fail:** 0
- **Lint:** 21 pre-existing E501 warnings, 0 new issues

## Traceability Matrix

| Bean AC | Test(s) | Status |
|---------|---------|--------|
| Compiled prompts include project context when project.md exists | `test_compile_injects_project_context`, `test_generate_injects_project_context_by_default` | PASS |
| Context injection is togglable (default: on) | `test_generation_options_inject_project_context_default`, `test_generation_options_inject_project_context_toggle`, `test_generate_skips_project_context_when_disabled` | PASS |
| Each persona's compiled prompt includes project overview | `test_compile_injects_project_context` (verified content appears) | PASS |
| Tests verify injection with and without project.md | `test_compile_injects_project_context`, `test_compile_omits_project_context_when_empty`, `test_compile_default_project_context_is_empty` | PASS |
| All tests pass | 323 passed | PASS |
| Lint clean | 0 new issues | PASS |

## Edge Cases Verified

| ID | Case | Test | Status |
|----|------|------|--------|
| EC-1 | Toggle true + file exists | `test_generate_injects_project_context_by_default` | PASS |
| EC-2 | Toggle true + file missing | `test_compile_default_project_context_is_empty` | PASS |
| EC-3 | Toggle false + file exists | `test_generate_skips_project_context_when_disabled` | PASS |
| EC-5 | Toggle omitted (default) | `test_generation_options_inject_project_context_default` | PASS |
| EC-6 | Empty project.md | `test_compile_omits_project_context_when_empty` | PASS |
| EC-6b | Whitespace-only project.md | `test_compile_omits_project_context_when_whitespace_only` | PASS |
| EC-8 | `{{ project_context }}` in persona.md | `test_jinja2_renders_project_context_variable` | PASS |
| EC-8b | `{{ project_context }}` when no context | `test_jinja2_project_context_empty_when_no_context` | PASS |

## Code Review Summary

### `foundry_app/core/models.py`
- Single field addition: `inject_project_context: bool = True` — clean, backward compatible

### `foundry_app/services/generator.py`
- Toggle check wraps existing `project.md` reading — minimal change, no logic restructuring
- When False, `project_context` stays `""` — compiler handles empty string gracefully

### `foundry_app/services/compiler.py`
- `project_context` added to Jinja2 `tpl_ctx` dict — one line, clean
- No changes to the section injection logic (lines 147-155) — still works via `.strip()` check

### Backward Compatibility
- Verified: old GenerationOptions YAML without `inject_project_context` defaults to `True`
- Verified: YAML round-trip preserves `False` value

## Findings

No issues found. Clean, minimal implementation.

## Recommendation

**GO** — All acceptance criteria met. 10 new tests with comprehensive edge case coverage. No regressions. Clean implementation.
