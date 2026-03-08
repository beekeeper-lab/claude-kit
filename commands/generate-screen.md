# /generate-screen Command

Generate responsive UI screens/pages from text descriptions, field definitions, diagrams, and style references. Code lands in your project's source tree.

## Usage

```
/generate-screen <description of what you want>
```

## Examples

| Command | What It Does |
|---------|-------------|
| `/generate-screen a customer profile page with contact info, address, and recent orders` | Full screen with auto-detected platform |
| `/generate-screen --platform react --framework tailwind a dashboard showing project metrics` | React + Tailwind dashboard |
| `/generate-screen --fields data/donor-fields.csv a donor intake form` | Form generated from field definitions |
| `/generate-screen --mermaid docs/workflow.mmd --mode plan-only a case management workflow` | Plan only, no code |
| `/generate-screen --style-ref src/pages/ExistingPage.tsx a settings page in the same style` | Match existing page style |
| `/generate-screen --with-tests --mode full-screen-plus-assets an onboarding wizard` | Full screen + tests + generated images |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--platform` | auto-detect | `react`, `pyside6`, `tkinter`, `flutter` |
| `--framework` | — | `tailwind`, `mui`, `shadcn`, `material` |
| `--mode` | `full-screen` | `plan-only`, `full-screen`, `full-screen-plus-assets` |
| `--with-tests` | off | Generate tests alongside the screen |
| `--screen-name` | inferred | Name for the screen/page |
| `--style-ref` | — | Reference image or code file (repeatable) |
| `--fields` | — | CSV or JSON field definitions |
| `--mermaid` | — | Mermaid diagram file |
| `--reuse` | `prefer-existing` | `strict`, `prefer-existing`, `mixed` |
| `--responsive` | `balanced` | `desktop-first`, `mobile-first`, `balanced` |
| `--image-policy` | `only-if-needed` | `none`, `only-if-needed`, `aggressive` |
| `--density` | `comfortable` | `compact`, `comfortable`, `spacious` |
| `--output-dir` | auto-detect | Override output location |

## Process

1. Ingest prompt, field definitions, diagrams, and style references
2. Auto-detect platform from repo (or ask if unclear)
3. Inspect repo for existing components, theme, and patterns
4. Plan the screen: field grouping, layout, responsiveness, component mapping
5. Generate code into the project's source tree
6. Generate image assets if needed (via generate-image skill)
7. Write SCREEN-MANIFEST.md documenting all decisions

## Notes

- Platform is auto-detected from repo signals (package.json, pyproject.toml, pubspec.yaml)
- Existing project components and styles are always preferred over creating new ones
- The screen plan is created before any code — this is the most important step
- A SCREEN-MANIFEST.md is always written documenting assumptions and decisions
- Requires `GEMINI_API_KEY` only if image generation is triggered
