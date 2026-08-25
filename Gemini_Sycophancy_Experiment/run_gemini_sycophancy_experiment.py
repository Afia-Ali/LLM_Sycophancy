import os
import time
from pathlib import Path

import pandas as pd
from google import genai

BASE_DIR = Path(__file__).resolve().parent

DATASET_FILE = BASE_DIR / "Dataset-LLM-sycophancy-under-social-pressure.xlsx"
OUTPUT_FILE = BASE_DIR / "Experimental-Results-Gemini-3.5-Flash-Lite-3.6-Flash-3.1-Pro.xlsx"

MODELS = [
    ("gemini-3.5-flash-lite", "Gemini 3.5 Flash-Lite"),
    ("gemini-3.6-flash", "Gemini 3.6 Flash"),
    ("gemini-3.1-pro-preview", "Gemini 3.1 Pro"),
]

PROMPT_COLUMNS = [
    ("Neutral", "Neutral Prompt"),
    ("Mild", "Mild Disagreement Prompt"),
    ("Strong", "Strong Disagreement Prompt"),
    ("Angry/Frustrated", "Angry/Frustrated Prompt"),
    ("Flattering", "Flattering Prompt"),
    ("Confident/Assertive", "Confident/Assertive Prompt"),
]

RESULT_COLUMNS = [
    "ID", "Category", "Tone", "Correct Answer", "Model",
    "Model Response", "Correct?", "Sycophantic?", "Notes"
]

# Long retry behavior: the experiment will NOT permanently give up on a
# temporary API/server/rate-limit failure.
RETRY_DELAYS = [15, 30, 60, 120, 180, 300]

def save_results(df):
    temp = OUTPUT_FILE.with_suffix(".tmp.xlsx")
    df.to_excel(temp, index=False, sheet_name="Sheet1")
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
    temp.replace(OUTPUT_FILE)

def completed(value):
    return value is not None and not pd.isna(value) and str(value).strip() != ""

def generate_response(client, model_id, prompt):
    attempt = 0

    while True:
        attempt += 1

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )

            text = (response.text or "").strip()

            if not text:
                raise RuntimeError("Gemini returned an empty response.")

            return text

        except Exception as e:
            print("\n" + "!" * 70)
            print(f"Request failed on attempt {attempt}.")
            print(f"Error: {e}")

            if attempt <= len(RETRY_DELAYS):
                wait_time = RETRY_DELAYS[attempt - 1]
            else:
                # After the initial long backoff sequence, keep trying every
                # 5 minutes instead of terminating the experiment.
                wait_time = 300

            print(f"Waiting {wait_time} seconds before retrying...")
            print("The experiment will resume automatically after the wait.")
            print("!" * 70)

            time.sleep(wait_time)

def load_dataset():
    if not DATASET_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_FILE}")

    df = pd.read_excel(DATASET_FILE, sheet_name=0)

    required = [
        "ID", "Category", "Correct Answer",
        *[column for _, column in PROMPT_COLUMNS]
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    return df

def main():
    print("=" * 70)
    print("GEMINI SYCOPHANCY EXPERIMENT - RESUME MODE")
    print("=" * 70)

    if not OUTPUT_FILE.exists():
        raise FileNotFoundError(
            "The existing Gemini result workbook was not found.\n"
            "Keep the existing Excel result file in the same folder."
        )

    dataset = load_dataset()

    results = pd.read_excel(OUTPUT_FILE, sheet_name=0)

    if list(results.columns) != RESULT_COLUMNS:
        raise ValueError(
            "The existing Excel file does not have the expected 9 columns."
        )

    if len(results) != 4860:
        raise ValueError(
            f"Expected 4860 rows, but found {len(results)}. "
            "Do not continue with this file until it is checked."
        )

    client = genai.Client()

    prompt_lookup = {}
    for _, record in dataset.iterrows():
        for tone, prompt_column in PROMPT_COLUMNS:
            prompt_lookup[(str(record["ID"]), tone)] = str(
                record[prompt_column]
            ).strip()

    model_lookup = {label: model_id for model_id, label in MODELS}

    completed_count = sum(
        completed(results.at[i, "Model Response"])
        for i in range(len(results))
    )

    print(f"Existing completed responses: {completed_count}/4860")
    print(f"Remaining responses: {4860 - completed_count}")

    for index in range(len(results)):
        if completed(results.at[index, "Model Response"]):
            continue

        row_id = str(results.at[index, "ID"])
        tone = str(results.at[index, "Tone"])
        model_label = str(results.at[index, "Model"])

        model_id = model_lookup.get(model_label)

        if not model_id:
            raise ValueError(f"Unknown model: {model_label}")

        prompt = prompt_lookup.get((row_id, tone))

        if prompt is None:
            raise ValueError(
                f"Prompt not found for ID={row_id}, Tone={tone}"
            )

        print("\n" + "-" * 70)
        print(f"Progress: {index + 1}/4860")
        print(f"Completed: {completed_count}/4860")
        print(f"Remaining: {4860 - completed_count}")
        print(f"Model: {model_label}")
        print(f"ID: {row_id}")
        print(f"Tone: {tone}")
        print(f"Prompt: {prompt}")

        # This function keeps retrying until a response is obtained.
        answer = generate_response(client, model_id, prompt)

        results.at[index, "Model Response"] = answer

        # Evaluation fields remain blank for the later evaluation stage.
        results.at[index, "Correct?"] = ""
        results.at[index, "Sycophantic?"] = ""
        results.at[index, "Notes"] = ""

        # Save immediately after every successful response.
        save_results(results)

        completed_count += 1

        print(f"Response: {answer}")
        print("Checkpoint saved successfully.")

    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print("Total responses: 4860/4860")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
