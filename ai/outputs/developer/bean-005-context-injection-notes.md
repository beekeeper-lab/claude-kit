# BEAN-005: Compiled Prompt Project Context — Implementation Notes

**Author:** Developer | **Date:** 2026-02-07 | **Bean:** BEAN-005

## What Changed

### 1. `foundry_app/core/models.py`
- Added `inject_project_context: bool = True` to `GenerationOptions`

### 2. `foundry_app/services/generator.py`
- Wrapped `project.md` reading in a `if composition.generation.inject_project_context:` check
- When toggle is False, `project_context` stays empty string — compiler omits the section

### 3. `foundry_app/services/compiler.py`
- Added `"project_context": project_context` to the Jinja2 template context dict (`tpl_ctx`)
- Library `.md` files can now use `{{ project_context }}` as a template variable
- The existing section injection (lines 147-155) continues to work unchanged

### 4. `tests/test_compiler.py`
- Added `GenerationOptions` import
- 8 new tests:
  - `test_compile_injects_project_context` — context appears in compiled prompt
  - `test_compile_omits_project_context_when_empty` — no section when empty
  - `test_compile_omits_project_context_when_whitespace_only` — whitespace-only treated as empty
  - `test_compile_default_project_context_is_empty` — default call omits section
  - `test_jinja2_renders_project_context_variable` — `{{ project_context }}` works in persona.md
  - `test_jinja2_project_context_empty_when_no_context` — renders as empty string
  - `test_generation_options_inject_project_context_default` — default is True
  - `test_generation_options_inject_project_context_toggle` — can set to False

## Deviations from Design

None — no Architect spec for this bean (skipped). Implementation follows BA requirements.

## Test Results

- **321 tests pass** (313 existing + 8 new)
- **Lint:** 21 pre-existing E501 warnings, 0 new issues
