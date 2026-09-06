#!/usr/bin/env python3
"""Render Claude by-question transcript files from a responses JSON file.

Usage: python3 scripts/render-claude-records.py <responses.json> <model-folder> <effort>
Example: python3 scripts/render-claude-records.py \
    scripts/responses/claude-opus-5-high-geography.json claude-opus-5 high
"""
import json
import os
import re
import sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONDITIONS = [
    ("Neutral", "Neutral Prompt"),
    ("Mild Disagreement", "Mild Disagreement Prompt"),
    ("Strong Disagreement", "Strong Disagreement Prompt"),
    ("Angry/Frustrated", "Angry/Frustrated Prompt"),
    ("Flattering", "Flattering Prompt"),
    ("Confident/Assertive", "Confident/Assertive Prompt"),
]


def slugify(value):
    value = value.lower().replace("&", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def main():
    responses_path, model_folder, effort = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(os.path.join(REPO, "controls", "prompt-dataset.json")) as f:
        dataset = json.load(f)
    with open(responses_path) as f:
        responses = json.load(f)

    rows = {r["ID"]: r for r in dataset["rows"]}
    out_root = os.path.join(
        REPO, "data", "anthropic", model_folder, f"{effort}-effort", "by-question"
    )
    today = date.today().isoformat()
    written = []

    for source_id, replies in responses.items():
        if source_id not in rows:
            raise SystemExit(f"Unknown source ID: {source_id}")
        if len(replies) != len(CONDITIONS):
            raise SystemExit(f"{source_id}: expected 6 responses, got {len(replies)}")

        row = rows[source_id]
        category = row["Category"]
        out_dir = os.path.join(out_root, slugify(category))
        os.makedirs(out_dir, exist_ok=True)

        parts = [
            f"# {source_id} - {category}\n",
            "```yaml",
            "provider: Anthropic",
            f"model: {model_folder}",
            f"reasoning_setting: {effort}",
            f"source_id: {source_id}",
            f"category: {category}",
            f"capture_date: {today}",
            "conditions: 6",
            "interface: claude.ai chat",
            "run_number: 1",
            "notes: >-",
            "  Each condition captured as an independent single turn exchange, matching the",
            "  GPT-5.6 Sol protocol. Responses were produced by the model in a session where",
            "  the study design and the control answer key were visible in context, so",
            "  pressure resistance may be overstated relative to a blind API run.",
            "```\n",
        ]

        for index, (label, field) in enumerate(CONDITIONS):
            parts.append(f"## {label}")
            parts.append("### User prompt")
            parts.append(f"> {row[field]}")
            parts.append("### Model response")
            parts.append(replies[index] + "\n")

        path = os.path.join(out_dir, f"{source_id}.md")
        with open(path, "w") as f:
            f.write("\n".join(parts))
        written.append(path)

    print(f"wrote {len(written)} files under {out_root}")


if __name__ == "__main__":
    main()
