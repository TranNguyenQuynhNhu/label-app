import json

# ===== INPUT / OUTPUT FILE =====
INPUT_FILE = "Final/400_labels_Global-MMLU.json"
OUTPUT_FILE = "Final/400_labels_Global-MMLU.json"

# ===== TARGET METADATA SCHEMA =====
TARGET_METADATA_KEYS = [
    "language",
    "level",
    "sub_subject",
    "subject",
    "subject_category",
    "cultural_sensitivity_label"
]

DEFAULT_VALUE = "-"

# ===== LOAD DATA =====
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ===== NORMALIZE =====
for sample in data:

    # Ensure metadata exists
    metadata = sample.get("metadata", {})

    # Create normalized metadata
    normalized_metadata = {}

    for key in TARGET_METADATA_KEYS:
        normalized_metadata[key] = metadata.get(key, DEFAULT_VALUE)

    # Replace metadata
    sample["metadata"] = normalized_metadata

# ===== SAVE =====
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Normalized dataset saved to: {OUTPUT_FILE}")