import json

INPUT_FILE = "Final/200_labels_SEA-EXAM.json"
OUTPUT_FILE = "Final/200_labels_SeaExam.json"

# All possible metadata keys
TARGET_METADATA_KEYS = [
    "language",
    "level",
    "sub_subject",
    "subject",
    "subject_category",
    "cultural_sensitivity_label",
    "category",
    "src",
    "question_id_src"
]

DEFAULT_VALUE = "-"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for sample in data:

    metadata = sample.get("metadata", {})

    normalized_metadata = {}

    for key in TARGET_METADATA_KEYS:

        value = metadata.get(key, DEFAULT_VALUE)

        # Convert non-string values to string
        if value is None:
            value = DEFAULT_VALUE

        normalized_metadata[key] = str(value)

    sample["metadata"] = normalized_metadata

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved normalized dataset to {OUTPUT_FILE}")