import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ============================================================
# 1. CONFIGURATION
# ============================================================

# File hiện tại đã có:
#
# SeaExam       = 2571
# Global-MMLU   = 4800
# MMLU-ProX     = 2700
# ---------------------
# TOTAL         = 10071
#
# KHÔNG chạy lại 3 dataset trên.
# Chỉ append VMLU.


INPUT_CSV = "annotations_raw_final.csv"

OUTPUT_CSV = "annotations_raw_final_with_vmlu.csv"


# ============================================================
# 3 FILE VMLU
#
# CHỈ CẦN THAY TÊN FILE Ở ĐÂY
# ============================================================

VMLU_FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Dong_1000_vmlu.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Vy_1000_vmlu.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_1000_vmlu.json",
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
            f"\nKhông tìm thấy file:\n{path}"
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


    # JSON dạng dictionary chứa list
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
        f"Không nhận diện được format JSON:\n{path}"
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
        # 2026-06-14T07:23:17.372Z

        timestamp_for_parse = timestamp.replace(
            "Z",
            "+00:00"
        )


        dt = datetime.fromisoformat(
            timestamp_for_parse
        )


        # Nếu timestamp không có timezone
        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )


        # Đưa về UTC
        dt = dt.astimezone(
            timezone.utc
        )


        # ISO 8601 với milliseconds
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


# File hiện tại phải có 10071 rows
if len(existing_rows) != 10071:

    print(
        f"[WARNING] File hiện tại có "
        f"{len(existing_rows)} rows."
    )

    print(
        "Expected: 10071 rows "
        "(SeaExam + Global-MMLU + MMLU-ProX)"
    )

else:

    print(
        "OK - Existing CSV có 10071 rows."
    )


# ============================================================
# 6. LOAD ONLY VMLU
# ============================================================

print("\n" + "=" * 70)
print("2. LOAD VMLU")
print("=" * 70)


vmlu_data_by_file = {}


for file_path in VMLU_FILES:

    data = load_json(file_path)

    vmlu_samples = []


    # ========================================================
    # QUAN TRỌNG:
    #
    # Không sort.
    # Giữ nguyên thứ tự sample trong JSON.
    # ========================================================

    for sample in data:

        benchmark_name = str(
            sample.get(
                "benchmark_name",
                ""
            )
        ).strip().lower()


        if benchmark_name in [
            "vmlu",
            "vmlu-v1",
            "vmlu_v1",
        ]:

            vmlu_samples.append(
                sample
            )


    vmlu_data_by_file[file_path] = (
        vmlu_samples
    )


    print(
        f"{file_path}: "
        f"{len(vmlu_samples)} samples"
    )


# ============================================================
# 7. CHECK 1000 SAMPLES / FILE
# ============================================================

print("\n" + "=" * 70)
print("CHECK VMLU COUNT")
print("=" * 70)


for file_path, samples in (
    vmlu_data_by_file.items()
):

    if len(samples) != 1000:

        print(
            f"[WARNING] {file_path}: "
            f"{len(samples)} samples "
            f"(expected 1000)"
        )

    else:

        print(
            f"OK - {file_path}: 1000 samples"
        )


# ============================================================
# 8. CHECK TIMESTAMP DUPLICATION
#
# Chỉ kiểm tra timestamp giống nhau
# GIỮA CÁC ANNOTATOR.
#
# Không coi timestamp giống nhau
# trong cùng một file là lỗi.
# ============================================================

print("\n" + "=" * 70)
print("CHECK TIMESTAMP DUPLICATION")
print("=" * 70)


timestamp_map = defaultdict(
    lambda: defaultdict(list)
)


for file_path, samples in (
    vmlu_data_by_file.items()
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


        # Timestamp giống nhau
        # giữa >= 2 annotator
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
# 9. CREATE VMLU ROWS
#
# Sample 1-500:
#   interval_id = 1
#   ontology_version = v2
#
# Sample 501-1000:
#   interval_id = 2
#   ontology_version = v3
#
#
# ORDER:
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
# ============================================================

print("\n" + "=" * 70)
print("3. CREATE VMLU ROWS")
print("=" * 70)


vmlu_rows = []


for position in range(1, 1001):


    # --------------------------------------------------------
    # INTERVAL + ONTOLOGY VERSION
    # --------------------------------------------------------

    if position <= 500:

        interval_id = "1"

        ontology_version = "v2"


    else:

        interval_id = "2"

        ontology_version = "v3"


    # --------------------------------------------------------
    # LẤY 3 ANNOTATOR Ở CÙNG POSITION
    # --------------------------------------------------------

    for file_path in VMLU_FILES:

        samples = vmlu_data_by_file[
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

        vmlu_rows.append({

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
# 10. CHECK VMLU TOTAL
# ============================================================

print("\n" + "=" * 70)
print("CHECK VMLU TOTAL")
print("=" * 70)


print(
    f"VMLU rows created: "
    f"{len(vmlu_rows)}"
)


print(
    "Expected: 1000 × 3 = 3000"
)


if len(vmlu_rows) == 3000:

    print(
        "OK - Có đúng 3000 rows."
    )

else:

    print(
        "[WARNING] Expected 3000 rows."
    )


# ============================================================
# 11. CHECK INTERVAL DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("VMLU INTERVAL SUMMARY")
print("=" * 70)


interval_counts = defaultdict(int)


for row in vmlu_rows:

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


print("\nExpected:")

print(
    "Interval 1 | v2 | 500 × 3 = 1500 rows"
)

print(
    "Interval 2 | v3 | 500 × 3 = 1500 rows"
)


# ============================================================
# 12. CHECK DUPLICATE TRONG VMLU
#
# Duplicate = item_id + annotator_id
# ============================================================

print("\n" + "=" * 70)
print("CHECK VMLU DUPLICATES")
print("=" * 70)


seen = set()

duplicates = []


for row in vmlu_rows:

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
# 13. CHECK VMLU ĐÃ CÓ TRONG CSV CHƯA
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


new_vmlu_rows = []

already_exists = []


for row in vmlu_rows:

    key = (
        row["item_id"],
        row["annotator_id"]
    )


    if key in existing_keys:

        already_exists.append(
            key
        )

    else:

        new_vmlu_rows.append(
            row
        )


if already_exists:

    print(
        f"[WARNING] Có "
        f"{len(already_exists)} VMLU "
        f"records đã tồn tại trong CSV."
    )

else:

    print(
        "OK - VMLU chưa tồn tại "
        "trong CSV."
    )


# ============================================================
# 14. APPEND VMLU
#
# KHÔNG ĐỤNG VÀO:
#   SeaExam
#   Global-MMLU
#   MMLU-ProX
# ============================================================

print("\n" + "=" * 70)
print("APPEND VMLU")
print("=" * 70)


final_rows = (
    existing_rows
    + new_vmlu_rows
)


print(
    f"Existing rows : "
    f"{len(existing_rows)}"
)


print(
    f"New VMLU rows : "
    f"{len(new_vmlu_rows)}"
)


print(
    f"Final rows    : "
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
    "SUCCESS!"
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
    "Existing datasets:"
)

print(
    "  SeaExam       = 2571 rows"
)

print(
    "  Global-MMLU   = 4800 rows"
)

print(
    "  MMLU-ProX     = 2700 rows"
)

print(
    "  -----------------------"
)

print(
    "  Existing total = 10071 rows"
)


print(
    "\nAdded:"
)

print(
    "  VMLU          = 3000 rows"
)


print(
    "\nExpected final:"
)

print(
    "  10071 + 3000 = 13071 rows"
)


expected_total = 13071


if len(final_rows) == expected_total:

    print(
        f"\nOK - Final CSV có đúng "
        f"{expected_total} rows."
    )

else:

    print(
        f"\n[WARNING] Final CSV có "
        f"{len(final_rows)} rows."
    )

    print(
        f"Expected: {expected_total}"
    )


print("\nDONE.")