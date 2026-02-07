# Task 02: Context Injection Implementation

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Implement the missing pieces: GenerationOptions toggle, Jinja2 template variable, and comprehensive tests for project context injection.

## Inputs

- `ai/beans/BEAN-005-member-prompt-context/bean.md` — problem statement
- `ai/outputs/ba/bean-005-context-injection-requirements.md` — requirements
- `foundry_app/services/compiler.py` — compiler (already has injection, needs Jinja2 var)
- `foundry_app/services/generator.py` — generator (already reads project.md, needs toggle check)
- `foundry_app/core/models.py` — GenerationOptions (needs toggle field)

## Acceptance Criteria

- [ ] `GenerationOptions` has an `inject_project_context` field (default: True)
- [ ] Generator respects the toggle (skips reading project.md when False)
- [ ] `{{ project_context }}` available as Jinja2 variable in library .md files
- [ ] Tests for: context injected, context omitted (toggle off), context omitted (no file), Jinja2 var
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — clean
- [ ] Implementation notes written to `ai/outputs/developer/bean-005-context-injection-notes.md`

## Definition of Done

Code changes complete, tests pass, lint clean. Ready for Tech-QA.
