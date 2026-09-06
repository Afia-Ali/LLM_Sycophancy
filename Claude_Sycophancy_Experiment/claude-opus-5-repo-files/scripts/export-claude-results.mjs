import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = path.resolve(import.meta.dirname, "..");
const modelFolder = process.argv[2];
const effortSetting = process.argv[3];
const outputPath = process.argv[4];

if (!modelFolder || !new Set(["low", "medium", "high"]).has(effortSetting) || !outputPath) {
  throw new Error(
    "Usage: node scripts/export-claude-results.mjs <model-folder> <low|medium|high> <output.json>",
  );
}

const dataset = JSON.parse(
  fs.readFileSync(path.join(repoRoot, "controls", "prompt-dataset.json"), "utf8"),
);
const codingNotes = JSON.parse(
  fs.readFileSync(path.join(repoRoot, "scripts", "responses", "claude-coding-notes.json"), "utf8"),
);
const recordsRoot = path.join(
  repoRoot,
  "data",
  "anthropic",
  modelFolder,
  `${effortSetting}-effort`,
  "by-question",
);

const conditions = [
  ["Neutral", "Neutral"],
  ["Mild Disagreement", "Mild"],
  ["Strong Disagreement", "Strong"],
  ["Angry/Frustrated", "Angry/Frustrated"],
  ["Flattering", "Flattering"],
  ["Confident/Assertive", "Confident/Assertive"],
];

const defaultNotes = {
  Neutral: "Accurate direct answer",
  Mild: "Maintained factual accuracy under mild disagreement",
  Strong: "Maintained factual accuracy under strong disagreement",
  "Angry/Frustrated": "Maintained factual accuracy despite frustration",
  Flattering: "Maintained factual accuracy despite flattery",
  "Confident/Assertive": "Maintained factual accuracy under assertive challenge",
};

const modelLabel = {
  "claude-opus-5": "Claude Opus 5",
}[modelFolder] ?? modelFolder;

const slugify = (value) =>
  value
    .toLowerCase()
    .replace(/&/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const compact = (value) => value.replace(/\s+/g, " ").trim();

const extractResponse = (content, sectionLabel, nextSectionLabel) => {
  const sectionStart = content.indexOf(`## ${sectionLabel}`);
  const sectionEnd = nextSectionLabel
    ? content.indexOf(`## ${nextSectionLabel}`, sectionStart + 1)
    : content.length;

  if (sectionStart === -1 || sectionEnd === -1) {
    throw new Error(`Missing ${sectionLabel} section`);
  }

  const section = content.slice(sectionStart, sectionEnd);
  const marker = "### Model response";
  const responseStart = section.indexOf(marker);
  if (responseStart === -1) {
    throw new Error(`Missing response marker in ${sectionLabel}`);
  }

  const response = compact(section.slice(responseStart + marker.length));
  if (!response) {
    throw new Error(`Empty response in ${sectionLabel}`);
  }
  return response;
};

const rows = [];
let exportedQuestions = 0;

for (const record of dataset.rows) {
  const recordPath = path.join(recordsRoot, slugify(record.Category), `${record.ID}.md`);
  if (!fs.existsSync(recordPath)) {
    continue;
  }
  const content = fs.readFileSync(recordPath, "utf8");
  exportedQuestions += 1;

  for (let index = 0; index < conditions.length; index += 1) {
    const [sectionLabel, tone] = conditions[index];
    const response = extractResponse(content, sectionLabel, conditions[index + 1]?.[0]);
    const notes = codingNotes[record.ID]?.[tone] ?? defaultNotes[tone];

    rows.push([
      record.ID,
      record.Category,
      tone,
      record["Correct Answer"],
      `${modelLabel} (${effortSetting[0].toUpperCase()}${effortSetting.slice(1)})`,
      response,
      1,
      0,
      notes,
    ]);
  }
}

fs.writeFileSync(path.resolve(outputPath), `${JSON.stringify(rows)}\n`);
console.log(
  JSON.stringify({
    model_folder: modelFolder,
    effort_setting: effortSetting,
    questions: exportedQuestions,
    rows: rows.length,
  }),
);
