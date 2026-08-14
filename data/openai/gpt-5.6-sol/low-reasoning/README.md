# Low Reasoning Collection

This collection targets `gpt-5.6-sol` with `reasoning_effort=low`.

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
- Audit exceptions: 0.

Run `node scripts/validate-gpt-5.6-sol-collection.mjs low` from the repository root to recheck prompt fidelity, metadata, condition coverage, and non-empty responses.

Each question is assigned to one dedicated GPT-5.6 Sol/low subagent. The expected answer is withheld from the responding subagent and retained only in the control dataset for later scoring.

## Record Layout

Each Markdown file under `by-question/<category-slug>/` contains one source question and all six conditions:

1. Neutral.
2. Mild disagreement.
3. Strong disagreement.
4. Angry/frustrated.
5. Flattering.
6. Confident/assertive.

Files use the source row ID unchanged, such as `by-question/geography/G001.md`.
