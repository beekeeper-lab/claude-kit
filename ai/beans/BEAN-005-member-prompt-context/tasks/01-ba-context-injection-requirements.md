# Task 01: Context Injection Requirements

| Field | Value |
|-------|-------|
| **Owner** | ba |
| **Status** | Done |
| **Depends On** | — |

## Goal

Refine the acceptance criteria for project context injection. The core mechanism already exists (generator reads project.md, compiler injects it). Define what's missing: toggle, Jinja2 variable, test coverage, edge cases.

## Inputs

- `ai/beans/BEAN-005-member-prompt-context/bean.md` — problem statement and initial AC
- `foundry_app/services/compiler.py` — already accepts `project_context` param and injects it
- `foundry_app/services/generator.py:165-175` — already reads `ai/context/project.md`
- `foundry_app/core/models.py` — `GenerationOptions` model (no toggle yet)

## Acceptance Criteria

- [ ] User stories covering: toggle on/off, Jinja2 variable in templates, missing project.md graceful handling
- [ ] Edge cases documented
- [ ] Scope boundary: what's already done vs what needs adding
- [ ] Output written to `ai/outputs/ba/bean-005-context-injection-requirements.md`

## Definition of Done

Requirements doc exists. Downstream personas can implement without ambiguity.
