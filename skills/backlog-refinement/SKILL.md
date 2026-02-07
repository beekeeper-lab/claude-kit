# Skill: Backlog Refinement

## Description

Turns raw ideas, feature descriptions, or broad vision text into one or more well-formed beans through an iterative dialogue. The Team Lead analyzes the input to identify distinct units of work, asks clarifying questions to understand scope and priority, then creates properly-formed beans using `/new-bean`. This is the primary intake mechanism for getting new work into the backlog.

## Trigger

- Invoked by the `/backlog-refinement` slash command.
- Should only be used by the Team Lead persona.
- Requires `ai/beans/_index.md` and `ai/beans/_bean-template.md` to exist.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| raw_text | Text | Yes | Free-form description of ideas, features, or vision from the user |
| dry_run | Boolean | No | If true, show proposed beans without creating them. Defaults to false. |

## Process

### Phase 1: Analysis

1. **Receive the raw text** -- Accept whatever the user provides. It may be a single sentence, bullet points, multiple paragraphs, or a stream-of-consciousness description.

2. **Read the existing backlog** -- Parse `ai/beans/_index.md` to understand:
   - What beans already exist (avoid duplicates)
   - Current priorities and status (understand the landscape)
   - Next available bean ID

3. **Identify work units** -- Analyze the text to find natural boundaries between distinct units of work. Look for:
   - Separate features or capabilities
   - Infrastructure vs. application concerns
   - Dependencies that suggest ordering
   - Different personas or skill sets required
   - Independent deliverables that could be verified separately

4. **Draft bean proposals** -- For each identified work unit, draft:
   - A working title
   - A one-line description
   - An initial priority guess (based on context clues)
   - Any obvious dependencies on other proposed beans or existing work

### Phase 2: Dialogue

5. **Present the initial breakdown** -- Show the user the proposed beans:
   ```
   I've identified N potential beans from your input:

   1. **[Title]** — [one-line description] (Priority: [guess])
   2. **[Title]** — [one-line description] (Priority: [guess])
   ...

   Let me ask some questions to refine these.
   ```

6. **Ask clarifying questions** -- For each proposed bean (or for the set as a whole), ask about areas that are unclear or need user input:
   - **Priority:** "How important is [X] relative to [Y]? Should it be High, Medium, or Low?"
   - **Scope:** "For [X], should we include [detail] or defer that?"
   - **Dependencies:** "Does [X] need [Y] to be done first, or are they independent?"
   - **Missing context:** "You mentioned [vague reference] — can you elaborate on what you mean by that?"
   - **Acceptance criteria:** "What does 'done' look like for [X]? What would you test?"
   - **Splitting:** "This seems like it might be two separate pieces of work: [A] and [B]. Should I split them?"
   - **Merging:** "[X] and [Y] seem closely related. Should they be one bean?"

   Ask questions in batches (2-4 at a time) to avoid overwhelming the user. Focus on the most important ambiguities first.

7. **Iterate** -- Based on the user's answers:
   - Adjust titles, descriptions, and priorities
   - Split beans that are too large or merge beans that are too small
   - Add details to scope and acceptance criteria
   - Identify new dependencies
   - Present the updated breakdown and ask follow-up questions if needed

   Continue until the user confirms the breakdown is complete. Look for signals like:
   - "Looks good"
   - "Yes, create those"
   - "That's right"
   - Explicit approval of the bean list

### Phase 3: Creation

8. **Check for dry run** -- If `dry_run` is true, skip creation and go to step 11.

9. **Create each bean** -- For each agreed-upon bean, invoke the `/new-bean` workflow:
   - Generate the next sequential bean ID
   - Create `ai/beans/BEAN-NNN-<slug>/bean.md` with all fields:
     - **Problem Statement:** Derived from the user's description and dialogue
     - **Goal:** What success looks like (from the user's acceptance criteria discussion)
     - **Scope:** In Scope and Out of Scope (from the dialogue)
     - **Acceptance Criteria:** Concrete, testable checklist items
     - **Priority:** As agreed in the dialogue
     - **Dependencies:** Noted in the Notes section if they depend on other beans
   - Update `ai/beans/_index.md` with the new entry

10. **Handle duplicates** -- If a proposed bean closely matches an existing bean:
    - Warn the user: "This looks similar to BEAN-NNN ([title]). Create it anyway?"
    - If the user says yes, create it
    - If the user says no, skip it

### Phase 4: Summary

11. **Present results** -- Show a summary table of all created (or proposed, if dry run) beans:
    ```
    Created N beans:

    | Bean ID | Title | Priority | Dependencies |
    |---------|-------|----------|-------------|
    | BEAN-012 | [Title] | High | — |
    | BEAN-013 | [Title] | Medium | BEAN-012 |
    ...

    Run `/bean-status` to see the full backlog.
    ```

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| new_beans | Markdown files | One or more `bean.md` files created via `/new-bean` |
| updated_index | Markdown file | `_index.md` updated with all new beans |
| summary | Console text | Table of created beans with IDs, titles, priorities, and dependencies |

## Quality Criteria

- Every created bean has a non-trivial Problem Statement (not just restating the title).
- Every bean has at least 3 acceptance criteria.
- Scope sections distinguish In Scope from Out of Scope.
- Dependencies between created beans are noted in their Notes sections.
- No duplicate beans are created without explicit user approval.
- The dialogue phase asks at least one clarifying question before creating beans.
- Bean IDs are sequential and do not collide with existing beans.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `EmptyInput` | No text provided by the user | Ask the user to describe what they want to build or change |
| `DuplicateBean` | Proposed bean matches an existing bean title or problem | Warn user and ask for explicit approval to create or skip |
| `UserAbort` | User decides to cancel | Exit without creating any beans; no changes to the backlog |
| `BacklogMissing` | `_index.md` does not exist | Create it first with `/new-bean` or check project setup |

## Dependencies

- Backlog index at `ai/beans/_index.md`
- Bean template at `ai/beans/_bean-template.md`
- `/new-bean` skill for creating individual beans
