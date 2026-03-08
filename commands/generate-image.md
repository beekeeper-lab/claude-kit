# /generate-image Command

Generate image assets from text prompts using Gemini's Nano Banana models.

## Usage

```
/generate-image <description of what you want>
```

## Examples

| Command | What It Does |
|---------|-------------|
| `/generate-image a hero image for Foundry with dark premium styling` | Draft-quality hero image using NB2 |
| `/generate-image a polished infographic of the deployment pipeline, final quality` | Final-quality infographic using Pro |
| `/generate-image 4 variations of a project dashboard icon` | 4 draft variations using NB2 |
| `/generate-image an icon like this reference image [path]` | Image based on a reference |

## Process

1. Parse the user's description into structured parameters
2. Invoke the `generate-image` skill
3. Report the generated file paths and model used

## Notes

- Default model is Nano Banana 2 (fast/cheap) — Pro is used for `final` quality or when explicitly requested
- Images are saved to `images/<context>/` with JSON metadata sidecars
- Requires `GEMINI_API_KEY` in environment or `.env` file
- Uses `uv run --with` for dependencies — no install needed
