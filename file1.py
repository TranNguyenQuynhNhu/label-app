import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ============================================================
# 1. CONFIGURATION
# ============================================================

# File hiện tại đã có:
# SeaExam     = 857 × 3   = 2571
# Global-MMLU = 1600 × 3  = 4800
# --------------------------------
# TOTAL                     = 7371
#
# KHÔNG chạy lại Global-MMLU.

INPUT_CSV = "annotations_raw_with_global_mmlu.csv"

# File output sau khi thêm MMLU-ProX
OUTPUT_CSV = "annotations_raw_final.csv"


# ============================================================
# 3 FILE MMLU-ProX
#
# CHỈ CẦN THAY TÊN FILE Ở ĐÂY
# ============================================================

MMLU_PROX_FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Dong_900_mmluprox.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Vy_900_mmluprox.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_900_mmluprox.json",
]


# ============================================================
# CSV COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "item_id",
    "source",
    "annotator_id",
    "cs_label",
    "to_label",
    "annotated_at",
    "interval_id",
    "ontology_version",
    "is_reevaluation",
    "triggered_refinement",
]


# ============================================================
# 2. LOAD JSON
# ============================================================

def load_json(path):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file:\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # JSON dạng list
    if isinstance(data, list):
        return data

    # JSON dạng dict chứa list
    if isinstance(data, dict):

        possible_keys = [
            "data",
            "samples",
            "annotations",
            "items",
        ]

        for key in possible_keys:

            if (
                key in data
                and isinstance(data[key], list)
            ):
                return data[key]

    raise ValueError(
        f"Không nhận diện được format JSON: {path}"
    )


# ============================================================
# 3. NORMALIZE TIMESTAMP
# ============================================================

def normalize_timestamp(timestamp):

    if timestamp is None:
        return ""

    timestamp = str(timestamp).strip()

    if timestamp == "":
        return ""

    try:

        # Ví dụ:
        # 2026-05-02T21:46:09.482Z

        timestamp_for_parse = timestamp.replace(
            "Z",
            "+00:00"
        )

        dt = datetime.fromisoformat(
            timestamp_for_parse
        )

        # Nếu không có timezone
        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        # Đưa về UTC
        dt = dt.astimezone(
            timezone.utc
        )

        # ISO 8601 milliseconds
        normalized = dt.isoformat(
            timespec="milliseconds"
        )

        # +00:00 -> Z
        normalized = normalized.replace(
            "+00:00",
            "Z"
        )

        return normalized

    except Exception as e:

        print(
            f"[WARNING] Không parse được timestamp: "
            f"{timestamp}"
        )

        print(
            f"          Error: {e}"
        )

        return timestamp


# ============================================================
# 4. READ EXISTING CSV
# ============================================================

print("\n" + "=" * 70)
print("1. READ EXISTING CSV")
print("=" * 70)

if not Path(INPUT_CSV).exists():

    raise FileNotFoundError(
        f"Không tìm thấy {INPUT_CSV}"
    )


with open(
    INPUT_CSV,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    existing_columns = reader.fieldnames
    existing_rows = list(reader)


print(
    f"Existing rows: {len(existing_rows)}"
)


# ============================================================
# 5. CHECK EXISTING CSV
# ============================================================

print("\n" + "=" * 70)
print("CHECK EXISTING DATA")
print("=" * 70)


# File hiện tại phải là 7371 dòng
if len(existing_rows) != 7371:

    print(
        f"[WARNING] File hiện tại có "
        f"{len(existing_rows)} rows."
    )

    print(
        "Expected: 7371 rows "
        "(SeaExam + Global-MMLU)"
    )

else:

    print(
        "OK - Existing CSV có 7371 rows."
    )


# ============================================================
# 6. LOAD ONLY MMLU-ProX
# ============================================================

print("\n" + "=" * 70)
print("2. LOAD MMLU-ProX")
print("=" * 70)


mmlu_prox_data_by_file = {}


for file_path in MMLU_PROX_FILES:

    data = load_json(file_path)

    mmlu_prox_samples = []

    # KHÔNG SORT
    # Giữ nguyên thứ tự xuất hiện trong file

    for sample in data:

        benchmark_name = str(
            sample.get(
                "benchmark_name",
                ""
            )
        ).strip().lower()

        if benchmark_name in [
            "mmlu-prox",
            "mmlu_prox",
            "mmlupro-x",
            "mmlupro_x",
            "mmlupro",
        ]:

            mmlu_prox_samples.append(
                sample
            )

    mmlu_prox_data_by_file[file_path] = (
        mmlu_prox_samples
    )

    print(
        f"{file_path}: "
        f"{len(mmlu_prox_samples)} samples"
    )


# ============================================================
# 7. CHECK 900 SAMPLES / FILE
# ============================================================

print("\n" + "=" * 70)
print("CHECK MMLU-ProX COUNT")
print("=" * 70)


for file_path, samples in (
    mmlu_prox_data_by_file.items()
):

    if len(samples) != 900:

        print(
            f"[WARNING] {file_path}: "
            f"{len(samples)} samples "
            f"(expected 900)"
        )

    else:

        print(
            f"OK - {file_path}: 900 samples"
        )


# ============================================================
# 8. CHECK TIMESTAMP TRÙNG GIỮA 3 ANNOTATOR
# ============================================================

print("\n" + "=" * 70)
print("CHECK TIMESTAMP DUPLICATION")
print("=" * 70)


timestamp_map = defaultdict(
    lambda: defaultdict(list)
)


for file_path, samples in (
    mmlu_prox_data_by_file.items()
):

    for sample in samples:

        sample_id = sample.get(
            "sample_id",
            ""
        )

        annotator = sample.get(
            "annotator",
            ""
        )

        raw_timestamp = sample.get(
            "timestamp",
            ""
        )

        if not sample_id:
            continue

        if not annotator:
            continue

        if not raw_timestamp:
            continue

        timestamp = normalize_timestamp(
            raw_timestamp
        )

        timestamp_map[
            sample_id
        ][
            timestamp
        ].append(
            annotator
        )


duplicate_timestamps = []


for sample_id, timestamp_groups in (
    timestamp_map.items()
):

    for timestamp, annotators in (
        timestamp_groups.items()
    ):

        unique_annotators = set(
            annotators
        )

        # Timestamp giống nhau giữa >= 2 annotator
        if len(unique_annotators) >= 2:

            duplicate_timestamps.append({

                "sample_id": sample_id,

                "timestamp": timestamp,

                "annotators": sorted(
                    unique_annotators
                ),
            })


if duplicate_timestamps:

    print(
        f"[WARNING] Có "
        f"{len(duplicate_timestamps)} "
        f"sample có timestamp giống nhau "
        f"giữa các annotator."
    )

    for item in duplicate_timestamps:

        print(
            f"\nSample ID : "
            f"{item['sample_id']}"
        )

        print(
            f"Timestamp : "
            f"{item['timestamp']}"
        )

        print(
            f"Annotators: "
            f"{item['annotators']}"
        )

else:

    print(
        "OK - Không có timestamp giống nhau "
        "giữa 3 annotator."
    )


# ============================================================
# 9. CREATE MMLU-ProX ROWS
#
# QUAN TRỌNG:
#
# Sample 1:
#   Khang
#   Ngoc
#   Nhu
#
# Sample 2:
#   Khang
#   Ngoc
#   Nhu
#
# ...
#
# Sample 400:
#   interval 1 / v2
#
# Sample 401:
#   interval 2 / v3
#
# ...
#
# Sample 900:
#   interval 2 / v3
# ============================================================

print("\n" + "=" * 70)
print("3. CREATE MMLU-ProX ROWS")
print("=" * 70)


mmlu_prox_rows = []


for position in range(1, 901):

    # --------------------------------------------------------
    # INTERVAL + ONTOLOGY
    # --------------------------------------------------------

    if position <= 400:

        interval_id = "1"
        ontology_version = "v2"

    else:

        interval_id = "2"
        ontology_version = "v3"


    # --------------------------------------------------------
    # LẤY 3 ANNOTATOR Ở CÙNG POSITION
    # --------------------------------------------------------

    for file_path in MMLU_PROX_FILES:

        samples = mmlu_prox_data_by_file[
            file_path
        ]

        if position > len(samples):

            print(
                f"[WARNING] {file_path}: "
                f"missing position "
                f"{position}"
            )

            continue


        sample = samples[
            position - 1
        ]


        # ----------------------------------------------------
        # TIMESTAMP -> annotated_at
        # ----------------------------------------------------

        annotated_at = normalize_timestamp(
            sample.get(
                "timestamp",
                ""
            )
        )


        # ----------------------------------------------------
        # CREATE ROW
        # ----------------------------------------------------

        mmlu_prox_rows.append({

            "item_id": sample.get(
                "sample_id",
                ""
            ),

            "source": sample.get(
                "benchmark_name",
                ""
            ),

            "annotator_id": sample.get(
                "annotator",
                ""
            ),

            "cs_label": sample.get(
                "cs_ca_label",
                ""
            ),

            "to_label": sample.get(
                "nat_tra_adp_label",
                ""
            ),

            "annotated_at": annotated_at,

            "interval_id": interval_id,

            "ontology_version": ontology_version,

            "is_reevaluation": "",

            "triggered_refinement": "",
        })


# ============================================================
# 10. CHECK MMLU-ProX TOTAL
# ============================================================

print("\n" + "=" * 70)
print("CHECK MMLU-ProX TOTAL")
print("=" * 70)


print(
    f"MMLU-ProX rows created: "
    f"{len(mmlu_prox_rows)}"
)

print(
    "Expected: 900 × 3 = 2700"
)


if len(mmlu_prox_rows) == 2700:

    print(
        "OK - Có đúng 2700 rows."
    )

else:

    print(
        "[WARNING] Expected 2700 rows."
    )


# ============================================================
# 11. CHECK INTERVAL DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("MMLU-ProX INTERVAL SUMMARY")
print("=" * 70)


interval_counts = defaultdict(int)


for row in mmlu_prox_rows:

    key = (
        row["interval_id"],
        row["ontology_version"]
    )

    interval_counts[key] += 1


for key, count in sorted(
    interval_counts.items()
):

    interval_id, ontology_version = key

    print(
        f"interval_id={interval_id} | "
        f"ontology_version={ontology_version} | "
        f"rows={count}"
    )


print(
    "\nExpected:"
)

print(
    "Interval 1 | v2 | 400 × 3 = 1200"
)

print(
    "Interval 2 | v3 | 500 × 3 = 1500"
)


# ============================================================
# 12. CHECK DUPLICATE
#
# Duplicate = item_id + annotator_id
# ============================================================

print("\n" + "=" * 70)
print("CHECK MMLU-ProX DUPLICATES")
print("=" * 70)


seen = set()
duplicates = []


for row in mmlu_prox_rows:

    key = (
        row["item_id"],
        row["annotator_id"]
    )

    if key in seen:

        duplicates.append(
            key
        )

    seen.add(
        key
    )


if duplicates:

    print(
        f"[WARNING] Có "
        f"{len(duplicates)} duplicate records."
    )

    for item_id, annotator in (
        duplicates[:20]
    ):

        print(
            f"{item_id} | {annotator}"
        )

else:

    print(
        "OK - Không có duplicate."
    )


# ============================================================
# 13. CHECK MMLU-ProX ĐÃ CÓ TRONG CSV CHƯA
# ============================================================

print("\n" + "=" * 70)
print("CHECK AGAINST EXISTING CSV")
print("=" * 70)


existing_keys = set()


for row in existing_rows:

    key = (
        row.get(
            "item_id",
            ""
        ),
        row.get(
            "annotator_id",
            ""
        )
    )

    existing_keys.add(
        key
    )


new_mmlu_prox_rows = []
already_exists = []


for row in mmlu_prox_rows:

    key = (
        row["item_id"],
        row["annotator_id"]
    )

    if key in existing_keys:

        already_exists.append(
            key
        )

    else:

        new_mmlu_prox_rows.append(
            row
        )


if already_exists:

    print(
        f"[WARNING] Có "
        f"{len(already_exists)} MMLU-ProX "
        f"records đã tồn tại trong CSV."
    )

else:

    print(
        "OK - MMLU-ProX chưa tồn tại "
        "trong CSV."
    )


# ============================================================
# 14. APPEND MMLU-ProX
#
# KHÔNG ĐỤNG VÀO GLOBAL-MMLU
# ============================================================

print("\n" + "=" * 70)
print("APPEND MMLU-ProX")
print("=" * 70)


final_rows = (
    existing_rows
    + new_mmlu_prox_rows
)


print(
    f"Existing rows       : "
    f"{len(existing_rows)}"
)

print(
    f"New MMLU-ProX rows  : "
    f"{len(new_mmlu_prox_rows)}"
)

print(
    f"Final rows          : "
    f"{len(final_rows)}"
)


# ============================================================
# 15. WRITE FINAL CSV
# ============================================================

print("\n" + "=" * 70)
print("WRITE FINAL CSV")
print("=" * 70)


try:

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=EXPECTED_COLUMNS
        )

        writer.writeheader()

        writer.writerows(
            final_rows
        )

except PermissionError:

    print(
        "[ERROR] Permission denied."
    )

    print(
        f"Hãy đóng {OUTPUT_CSV} "
        "nếu đang mở bằng Excel."
    )

    raise


print(
    f"SUCCESS!"
)

print(
    f"Output file: {OUTPUT_CSV}"
)


# ============================================================
# 16. FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL CHECK")
print("=" * 70)


print(
    "Existing:"
)

print(
    "  SeaExam       = 2571 rows"
)

print(
    "  Global-MMLU   = 4800 rows"
)

print(
    "  Existing total = 7371 rows"
)

print(
    "\nAdded:"
)

print(
    "  MMLU-ProX     = 2700 rows"
)

print(
    "\nExpected final:"
)

print(
    "  7371 + 2700 = 10071 rows"
)


if len(final_rows) == 10071:

    print(
        "\nOK - Final CSV có đúng "
        "10071 rows."
    )

else:

    print(
        f"\n[WARNING] Final CSV có "
        f"{len(final_rows)} rows."
    )

    print(
        "Expected: 10071"
    )


print("\nDONE.")