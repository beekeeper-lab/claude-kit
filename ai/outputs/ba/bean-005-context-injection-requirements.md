# BEAN-005: Compiled Prompt Project Context — Requirements

**Author:** BA | **Date:** 2026-02-07 | **Bean:** BEAN-005

## Current State

The core context injection mechanism **already works**:
- `generator.py:165-175` reads `ai/context/project.md` if it exists
- `compiler.py:147-155` injects it as a `## Project Context` section in each compiled prompt
- All 5 Foundry member prompts already contain the full project context

**What's missing:**
1. No toggle to disable context injection
2. `project_context` is not available as a Jinja2 template variable in library .md files
3. No compiler tests specifically covering context injection

## User Stories

### US-1: Disable project context injection

**As a** project creator who wants leaner compiled prompts,
**I want to** disable project context injection via the composition spec,
**So that** compiled prompts don't include the project.md content.

**Given** a composition YAML with `generation.inject_project_context: false`
**When** I run `foundry-cli generate`
**Then** the compiled member prompts do not contain a `## Project Context` section

### US-2: Default behavior includes context

**As a** project creator with a `project.md` file,
**I want to** have project context automatically included without configuration,
**So that** agents get project awareness out of the box.

**Given** a composition YAML without `inject_project_context` specified
**And** `ai/context/project.md` exists
**When** I run `foundry-cli generate`
**Then** the compiled member prompts include the project context (default: on)

### US-3: Graceful handling when project.md is missing

**As a** project creator who hasn't written a project.md yet,
**I want to** generation to proceed without errors,
**So that** I can add project context later.

**Given** a composition YAML with `generation.inject_project_context: true` (or default)
**And** `ai/context/project.md` does not exist
**When** I run `foundry-cli generate`
**Then** the compiled member prompts omit the `## Project Context` section (no error, no empty section)

### US-4: Jinja2 template variable in library files

**As a** library author writing persona .md files,
**I want to** reference `{{ project_context }}` in templates,
**So that** I can conditionally embed project-specific guidance within persona content.

**Given** a persona's `persona.md` contains `{{ project_context }}`
**When** the compiler processes it
**Then** the placeholder is replaced with the contents of `project.md`

## Scope Boundary

### In Scope
- `inject_project_context: bool` field on `GenerationOptions` (default: `true`)
- Generator respects the toggle when reading `project.md`
- `project_context` added to Jinja2 template context in compiler
- Tests for: injection on (with file), injection off (toggle), no file (graceful), Jinja2 variable

### Out of Scope
- Per-persona context control (all personas get the same context or none)
- Wizard UI for the toggle (GenerationOptions are not currently exposed in the wizard)
- Auto-generating project.md content from the codebase

## Edge Cases

| ID | Case | Expected Behavior |
|----|------|-------------------|
| EC-1 | Toggle true + file exists | Context injected (normal path) |
| EC-2 | Toggle true + file missing | No context section, no error |
| EC-3 | Toggle false + file exists | No context section (explicitly disabled) |
| EC-4 | Toggle false + file missing | No context section |
| EC-5 | Toggle omitted (default) | Same as true — context injected if file exists |
| EC-6 | Empty project.md (0 bytes) | No context section (empty string is falsy, `.strip()` check handles it) |
| EC-7 | project.md with Jinja2 syntax | Content is rendered as Jinja2 before injection (existing behavior of `_render_template`) |
| EC-8 | `{{ project_context }}` in persona.md | Replaced with project.md contents during Jinja2 rendering |
