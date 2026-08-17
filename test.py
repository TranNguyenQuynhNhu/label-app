from datasets import load_dataset
import pandas as pd
import ast
from collections import Counter, defaultdict

# ============================================================
# CONFIG
# ============================================================

FILTERED_DATASET = "trannguyenquynhnhu/SEA-Instruct-2602-fine-tuned"
ORIGINAL_DATASET = "aisingapore/SEA-Instruct-2602"


# ============================================================
# 1. LOAD FILTERED DATASET - 509,070 SAMPLES
# ============================================================

print("=" * 70)
print("1. LOADING FILTERED DATASET")
print("=" * 70)

filtered_ds = load_dataset(
    FILTERED_DATASET,
    split="train"
)

filtered_ids = filtered_ds["conversations_id"]

print(f"Filtered rows: {len(filtered_ids):,}")


# ============================================================
# 2. CHECK DUPLICATES IN FILTERED DATASET
# ============================================================

filtered_id_counts = Counter(filtered_ids)

filtered_duplicates = {
    conv_id: count
    for conv_id, count in filtered_id_counts.items()
    if count > 1
}

print(f"Unique IDs: {len(filtered_id_counts):,}")
print(f"Duplicate IDs: {len(filtered_duplicates):,}")

if filtered_duplicates:

    print("\nDuplicate IDs:")

    for conv_id, count in filtered_duplicates.items():
        print(f"  {conv_id} -> {count} occurrences")


# ============================================================
# 3. LOAD ORIGINAL VIETNAMESE DATASET
# ============================================================

print("\n" + "=" * 70)
print("2. LOADING ORIGINAL VIETNAMESE DATASET")
print("=" * 70)

original_ds = load_dataset(
    ORIGINAL_DATASET,
    "Vietnamese",
    split="train"
)

print(
    f"Original rows: "
    f"{len(original_ds):,}"
)


# ============================================================
# 4. BUILD METADATA LOOKUP FROM ORIGINAL
# ============================================================
#
# IMPORTANT:
# Không dùng dictionary ID -> metadata duy nhất,
# vì original có duplicate IDs.
#
# Thay vào đó:
#
# ID -> [metadata1, metadata2, ...]
#
# để giữ đúng số occurrence.
# ============================================================

print("\n" + "=" * 70)
print("3. BUILDING ORIGINAL METADATA LOOKUP")
print("=" * 70)

original_lookup = defaultdict(list)

for row in original_ds:

    conv_id = row["conversations_id"]

    original_lookup[conv_id].append({
        "prompt_primary_language":
            row["prompt_primary_language"],

        "prompt_region_scope":
            row["prompt_region_scope"]
    })


# ============================================================
# 5. CHECK DUPLICATES IN ORIGINAL
# ============================================================

original_duplicates = {
    conv_id: len(rows)
    for conv_id, rows in original_lookup.items()
    if len(rows) > 1
}

print(
    f"Unique IDs in original: "
    f"{len(original_lookup):,}"
)

print(
    f"Duplicate IDs in original: "
    f"{len(original_duplicates):,}"
)


# ============================================================
# 6. MATCH 509,070 ROWS
# ============================================================
#
# Quan trọng:
# Duyệt THEO THỨ TỰ của filtered dataset.
#
# Nếu filtered có:
#
# ID_A
# ID_A
#
# thì original_lookup[ID_A] có:
#
# metadata_A1
# metadata_A2
#
# ta lấy lần lượt A1 -> A2.
#
# Như vậy vẫn giữ nguyên 509,070 rows.
# ============================================================

print("\n" + "=" * 70)
print("4. MATCHING FILTERED DATASET WITH ORIGINAL")
print("=" * 70)

# Theo dõi đã sử dụng occurrence thứ mấy của mỗi ID
used_occurrences = Counter()

matched = []
missing_ids = []
insufficient_occurrences = []

for conv_id in filtered_ids:

    occurrence_index = used_occurrences[conv_id]

    original_rows = original_lookup.get(conv_id)

    # ID không tồn tại trong original
    if original_rows is None:

        missing_ids.append(conv_id)
        continue

    # Original có ít occurrence hơn filtered
    if occurrence_index >= len(original_rows):

        insufficient_occurrences.append(conv_id)
        continue

    metadata = original_rows[occurrence_index]

    matched.append({
        "conversations_id": conv_id,

        "prompt_primary_language":
            metadata["prompt_primary_language"],

        "prompt_region_scope":
            metadata["prompt_region_scope"]
    })

    used_occurrences[conv_id] += 1


# ============================================================
# 7. MATCHING RESULT
# ============================================================

print(f"Filtered rows       : {len(filtered_ids):,}")
print(f"Matched rows        : {len(matched):,}")
print(f"Missing IDs         : {len(missing_ids):,}")
print(
    f"Insufficient occurrences: "
    f"{len(insufficient_occurrences):,}"
)


# ============================================================
# 8. VERIFY THAT WE STILL HAVE EXACTLY 509,070 ROWS
# ============================================================

if len(matched) == len(filtered_ids):

    print(
        "\nSUCCESS: All 509,070 rows were matched "
        "without deduplication."
    )

else:

    print(
        "\nWARNING: Number of matched rows "
        "does NOT equal filtered rows."
    )


# ============================================================
# 9. CONVERT TO DATAFRAME
# ============================================================

df = pd.DataFrame(matched)


# ============================================================
# 10. CHECK VIETNAMESE LANGUAGE
# ============================================================

print("\n" + "=" * 70)
print("5. VIETNAMESE LANGUAGE")
print("=" * 70)

df["is_vietnamese"] = (
    df["prompt_primary_language"]
    .astype(str)
    .str.strip()
    .eq("Vietnamese")
)

num_vietnamese = int(
    df["is_vietnamese"].sum()
)


# ============================================================
# 11. CHECK VIETNAMESE CULTURAL CONTENT
# ============================================================

print("\n" + "=" * 70)
print("6. VIETNAMESE CULTURAL CONTENT")
print("=" * 70)


def contains_vietnam(value):

    if value is None:
        return False

    # Missing value
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        pass

    # List
    if isinstance(value, list):
        return "Vietnam" in value

    # String
    if isinstance(value, str):

        value = value.strip()

        # "Vietnam"
        if value == "Vietnam":
            return True

        # "['Vietnam', 'Thailand']"
        if value.startswith("[") and value.endswith("]"):

            try:

                parsed = ast.literal_eval(value)

                if isinstance(parsed, list):
                    return "Vietnam" in parsed

            except (ValueError, SyntaxError):
                pass

    return False


df["is_vietnamese_culture"] = (
    df["prompt_region_scope"]
    .apply(contains_vietnam)
)

num_vietnamese_culture = int(
    df["is_vietnamese_culture"].sum()
)


# ============================================================
# 12. CALCULATE RATIOS
# ============================================================

total = len(filtered_ds)

vietnamese_ratio = (
    num_vietnamese / total * 100
)

vietnamese_culture_ratio = (
    num_vietnamese_culture / total * 100
)


# ============================================================
# 13. FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(
    f"Total fine-tuned samples       : "
    f"{total:,}"
)

print(
    f"Matched samples                : "
    f"{len(df):,}"
)

print("-" * 70)

print(
    f"Vietnamese language            : "
    f"{num_vietnamese:,} "
    f"({vietnamese_ratio:.2f}%)"
)

print(
    f"Vietnamese cultural scope      : "
    f"{num_vietnamese_culture:,} "
    f"({vietnamese_culture_ratio:.2f}%)"
)

print("=" * 70)


# ============================================================
# 14. CHECK MISSING / PROBLEMATIC CASES
# ============================================================

if missing_ids:

    print("\nWARNING - Missing IDs:")
    for conv_id in missing_ids[:20]:
        print(conv_id)

if insufficient_occurrences:

    print("\nWARNING - Insufficient occurrences:")
    for conv_id in insufficient_occurrences[:20]:
        print(conv_id)


# ============================================================
# 15. SAVE DETAILED RESULT
# ============================================================

output_file = "SEA_Instruct_509070_language_region_analysis.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print(
    f"\nDetailed result saved to: "
    f"{output_file}"
)