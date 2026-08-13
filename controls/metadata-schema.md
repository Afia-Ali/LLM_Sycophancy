# Metadata Schema

Every transcript should begin with these fields.

```yaml
control_id:
provider:
model_folder:
reported_model_name:
model_id_or_label:
reasoning_setting:
tone_condition:
interface:
account_tier:
temperature:
top_p:
system_or_custom_instructions:
capture_date:
captured_by:
run_number:
conversation_url_or_id:
notes:
```

Use `unknown` when a value is unavailable. Do not leave required fields blank.

## Field Notes

- `reported_model_name`: The exact label shown in the UI or API response.
- `model_id_or_label`: The API model ID if known; otherwise repeat the UI label.
- `reasoning_setting`: Use the exact setting name, such as `medium`, `high`, `thinking_level=medium`, or `effort=high`.
- `system_or_custom_instructions`: Note any user-visible custom instructions or project instructions that might affect behavior.
- `conversation_url_or_id`: Optional. Do not include private URLs if sharing the dataset publicly.
