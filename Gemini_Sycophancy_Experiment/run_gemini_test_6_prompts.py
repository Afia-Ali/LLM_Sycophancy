import pandas as pd
import time
from google import genai

DATASET = "Dataset-LLM-sycophancy-under-social-pressure.xlsx"
OUTPUT = "Gemini_Test_6_Prompts.xlsx"

PROMPTS = [
    ("Neutral", "Neutral Prompt"),
    ("Mild", "Mild Disagreement Prompt"),
    ("Strong", "Strong Disagreement Prompt"),
    ("Angry/Frustrated", "Angry/Frustrated Prompt"),
    ("Flattering", "Flattering Prompt"),
    ("Confident/Assertive", "Confident/Assertive Prompt"),
]

client = genai.Client()
df = pd.read_excel(DATASET)
row = df.iloc[0]

results = []

for tone, column in PROMPTS:
    prompt = str(row[column]).strip()

    print("\n" + "=" * 60)
    print("ID:", row["ID"])
    print("Tone:", tone)
    print("Prompt:", prompt)

    for attempt in range(1, 7):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            answer = (response.text or "").strip()
            print("Response:", answer)
            break

        except Exception as e:
            print(f"Attempt {attempt}/6 failed: {e}")

            if attempt == 6:
                raise

            wait_time = attempt * 10
            print(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)

    results.append({
        "ID": row["ID"],
        "Category": row["Category"],
        "Tone": tone,
        "Correct Answer": row["Correct Answer"],
        "Model": "Gemini 3.6 Flash",
        "Model Response": answer,
        "Correct?": "",
        "Sycophantic?": "",
        "Notes": ""
    })

pd.DataFrame(results).to_excel(OUTPUT, index=False)

print("\nTEST COMPLETE.")
print("Created:", OUTPUT)