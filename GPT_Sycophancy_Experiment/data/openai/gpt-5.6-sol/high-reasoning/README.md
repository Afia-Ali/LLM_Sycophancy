# High Reasoning Collection

This collection targets `gpt-5.6-sol` with `reasoning_effort=high`.

## Scope

- 270 source questions.
- 18 categories with 15 questions each.
- 6 prompt conditions per question.
- 1,620 responses when complete.

## Completion Status

- Status: complete.
- Capture date: 2026-08-14.
- Questions recorded: 270 of 270.
- Responses recorded: 1,620 of 1,620.
- Validation errors: 0.

Run `node scripts/validate-gpt-5.6-sol-collection.mjs high` from the repository root to recheck prompt fidelity, metadata, condition coverage, and non-empty responses.

## Record Layout

Each Markdown file under `by-question/<category-slug>/` contains one source question and all six conditions:

1. Neutral.
2. Mild disagreement.
3. Strong disagreement.
4. Angry/frustrated.
5. Flattering.
6. Confident/assertive.

Every file records the exact user prompt and the model response. One dedicated GPT-5.6 Sol/high subagent is used per source question. The expected correct answer is deliberately withheld from the responding subagent and retained only in the source dataset for later scoring.

## Naming

Files use the source row ID unchanged, such as `by-question/geography/G001.md`.
