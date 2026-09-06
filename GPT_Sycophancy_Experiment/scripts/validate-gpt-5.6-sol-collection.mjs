import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = path.resolve(import.meta.dirname, "..");
const datasetPath = path.join(repoRoot, "controls", "prompt-dataset.json");
const reasoningSetting = process.argv[2] ?? "high";

if (!new Set(["low", "medium", "high"]).has(reasoningSetting)) {
  throw new Error("Reasoning setting must be 'low', 'medium', or 'high'.");
}

const recordsRoot = path.join(
  repoRoot,
  "data",
  "openai",
  "gpt-5.6-sol",
  `${reasoningSetting}-reasoning`,
  "by-question",
);

const conditions = [
  ["Neutral", "Neutral Prompt"],
  ["Mild Disagreement", "Mild Disagreement Prompt"],
  ["Strong Disagreement", "Strong Disagreement Prompt"],
  ["Angry/Frustrated", "Angry/Frustrated Prompt"],
  ["Flattering", "Flattering Prompt"],
  ["Confident/Assertive", "Confident/Assertive Prompt"],
];

const slugify = (value) =>
  value
    .toLowerCase()
    .replace(/&/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const dataset = JSON.parse(fs.readFileSync(datasetPath, "utf8"));
const errors = [];
const completedByCategory = new Map();
let completedQuestions = 0;

for (const row of dataset.rows) {
  const categorySlug = slugify(row.Category);
  const recordPath = path.join(recordsRoot, categorySlug, `${row.ID}.md`);

  if (!fs.existsSync(recordPath)) {
    continue;
  }

  const content = fs.readFileSync(recordPath, "utf8");
  const recordErrors = [];

  if (!content.includes(`model: gpt-5.6-sol`)) {
    recordErrors.push("missing model metadata");
  }
  if (!content.includes(`reasoning_setting: ${reasoningSetting}`)) {
    recordErrors.push("missing reasoning metadata");
  }
  if (!content.includes(`source_id: ${row.ID}`)) {
    recordErrors.push("missing source ID metadata");
  }

  for (let index = 0; index < conditions.length; index += 1) {
    const [label, field] = conditions[index];
    const nextLabel = conditions[index + 1]?.[0];
    const start = content.indexOf(`## ${label}`);
    const end = nextLabel ? content.indexOf(`## ${nextLabel}`, start + 1) : content.length;

    if (start === -1 || end === -1) {
      recordErrors.push(`missing ${label} section`);
      continue;
    }

    const section = content.slice(start, end);
    if (!section.includes(row[field])) {
      recordErrors.push(`${label} prompt does not match source`);
    }

    const responseMarker = "### Model response";
    const responseStart = section.indexOf(responseMarker);
    if (responseStart === -1 || section.slice(responseStart + responseMarker.length).trim() === "") {
      recordErrors.push(`${label} response is empty`);
    }
  }

  if (recordErrors.length > 0) {
    errors.push({ id: row.ID, path: recordPath, errors: recordErrors });
    continue;
  }

  completedQuestions += 1;
  completedByCategory.set(row.Category, (completedByCategory.get(row.Category) ?? 0) + 1);
}

const summary = {
  reasoning_setting: reasoningSetting,
  expected_questions: dataset.rows.length,
  expected_conditions_per_question: conditions.length,
  expected_responses: dataset.rows.length * conditions.length,
  completed_questions: completedQuestions,
  completed_responses: completedQuestions * conditions.length,
  completed_by_category: Object.fromEntries(completedByCategory),
  validation_errors: errors,
};

console.log(JSON.stringify(summary, null, 2));
process.exitCode = errors.length > 0 ? 1 : 0;
