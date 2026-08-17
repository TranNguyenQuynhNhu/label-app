import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ============================================================
# 1. CONFIGURATION
# ============================================================

# CSV đã tạo ở bước trước, chứa SeaExam
INPUT_CSV = "annotations_raw.csv"

# File output sau khi nối thêm Global-MMLU
OUTPUT_CSV = "annotations_raw_with_global_mmlu.csv"

# 3 file annotation JSON
FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Khang_1600_globalmmlu.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Ngoc_1600_globalmmlu.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_1600_globalmmlu.json",
]


# ============================================================
# 2. EXPECTED COLUMNS
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
# 3. LOAD JSON
# ============================================================

def load_json(path):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # Trường hợp JSON là list trực tiếp
    if isinstance(data, list):
        return data

    # Trường hợp JSON là dictionary chứa list
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
# 4. NORMALIZE TIMESTAMP
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
        #
        # Python fromisoformat cần +00:00
        timestamp_for_parse = timestamp.replace(
            "Z",
            "+00:00"
        )

        dt = datetime.fromisoformat(
            timestamp_for_parse
        )

        # Nếu timestamp không có timezone
        if dt.tzinfo is None:

            print(
                f"[WARNING] Timestamp không có timezone: "
                f"{timestamp}"
            )

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

        # +00:00 → Z
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
# 5. READ EXISTING CSV
# ============================================================

print("=" * 70)
print("READ EXISTING CSV")
print("=" * 70)

if not Path(INPUT_CSV).exists():

    raise FileNotFoundError(
        f"Không tìm thấy file {INPUT_CSV}"
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

print(
    f"Existing columns: {existing_columns}"
)


# ============================================================
# 6. CHECK EXISTING CSV COLUMNS
# ============================================================

if existing_columns != EXPECTED_COLUMNS:

    print(
        "\n[WARNING] Columns của CSV hiện tại "
        "khác với expected columns."
    )

    print(
        f"Current : {existing_columns}"
    )

    print(
        f"Expected: {EXPECTED_COLUMNS}"
    )

else:

    print(
        "OK - CSV columns đúng."
    )


# ============================================================
# 7. LOAD ALL 3 JSON FILES
# ============================================================

print("\n" + "=" * 70)
print("LOADING ANNOTATION FILES")
print("=" * 70)

file_data = {}

for file_path in FILES:

    data = load_json(file_path)

    file_data[file_path] = data

    print(
        f"{file_path}: {len(data)} samples"
    )


# ============================================================
# 8. CHECK TIMESTAMP DUPLICATION
#
# Chỉ kiểm tra:
# cùng sample_id
# + timestamp giống nhau
# + giữa các annotator
#
# KHÔNG kiểm tra timestamp trùng trong cùng 1 file.
# ============================================================

print("\n" + "=" * 70)
print(
    "CHECK SAME TIMESTAMP ACROSS ANNOTATORS"
)
print("=" * 70)


# sample_id
#   -> timestamp
#       -> annotators
timestamp_map = defaultdict(
    lambda: defaultdict(list)
)


for file_path, data in file_data.items():

    for sample in data:

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

        normalized_timestamp = (
            normalize_timestamp(
                raw_timestamp
            )
        )

        timestamp_map[
            sample_id
        ][
            normalized_timestamp
        ].append(
            annotator
        )


duplicate_timestamps = []


for sample_id, timestamp_groups in timestamp_map.items():

    for timestamp, annotators in timestamp_groups.items():

        # Timestamp xuất hiện ở >= 2 annotator
        unique_annotators = set(
            annotators
        )

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
        f"[WARNING] Phát hiện "
        f"{len(duplicate_timestamps)} sample "
        f"có timestamp giống nhau giữa "
        f"các annotator."
    )

    for item in duplicate_timestamps:

        print("\n" + "-" * 60)

        print(
            f"sample_id : {item['sample_id']}"
        )

        print(
            f"timestamp : {item['timestamp']}"
        )

        print(
            f"annotators: {item['annotators']}"
        )

else:

    print(
        "OK - Không có timestamp giống nhau "
        "giữa các annotator."
    )


# ============================================================
# 9. CREATE GLOBAL-MMLU ROWS
#
# OUTPUT ORDER:
#
# Sample 1:
#   Annotator 1
#   Annotator 2
#   Annotator 3
#
# Sample 2:
#   Annotator 1
#   Annotator 2
#   Annotator 3
#
# ...
#
# Sample 1600:
#   Annotator 1
#   Annotator 2
#   Annotator 3
# ============================================================

print("\n" + "=" * 70)
print("CREATE GLOBAL-MMLU ROWS")
print("=" * 70)


# ------------------------------------------------------------
# 9.1 Lấy Global-MMLU theo thứ tự trong từng file
# ------------------------------------------------------------

global_data_by_file = {}

for file_path, data in file_data.items():

    global_samples = []

    for sample in data:

        benchmark_name = str(
            sample.get(
                "benchmark_name",
                ""
            )
        ).strip().lower()

        if benchmark_name == "global-mmlu":

            global_samples.append(sample)

    global_data_by_file[file_path] = global_samples

    print(
        f"{file_path}: "
        f"{len(global_samples)} Global-MMLU samples"
    )


# ------------------------------------------------------------
# 9.2 CHECK MỖI FILE CÓ ĐÚNG 1600 SAMPLE
# ------------------------------------------------------------

for file_path, samples in global_data_by_file.items():

    if len(samples) != 1600:

        print(
            f"[WARNING] {file_path} có "
            f"{len(samples)} Global-MMLU samples, "
            f"expected 1600."
        )

    else:

        print(
            f"OK - {file_path}: 1600 samples"
        )


# ------------------------------------------------------------
# 9.3 TẠO ROW THEO SAMPLE POSITION
# ------------------------------------------------------------

global_rows = []


for position in range(1, 1601):

    # --------------------------------------------------------
    # INTERVAL + ONTOLOGY
    # --------------------------------------------------------

    if 1 <= position <= 200:

        interval_id = "1"
        ontology_version = "v1"

    elif 201 <= position <= 600:

        interval_id = "2"
        ontology_version = "v2"

    elif 601 <= position <= 1100:

        interval_id = "3"
        ontology_version = "v3"

    elif 1101 <= position <= 1600:

        interval_id = "4"
        ontology_version = "v3"

    else:

        interval_id = ""
        ontology_version = ""


    # --------------------------------------------------------
    # LẤY SAMPLE TỪNG ANNOTATOR Ở CÙNG POSITION
    # --------------------------------------------------------

    for file_path in FILES:

        samples = global_data_by_file[
            file_path
        ]

        # Nếu file thiếu sample
        if position > len(samples):

            print(
                f"[WARNING] {file_path}: "
                f"missing Global-MMLU "
                f"position {position}"
            )

            continue


        sample = samples[
            position - 1
        ]


        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        raw_timestamp = sample.get(
            "timestamp",
            ""
        )

        annotated_at = normalize_timestamp(
            raw_timestamp
        )


        # ----------------------------------------------------
        # CREATE ROW
        # ----------------------------------------------------

        global_rows.append({

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
# 9.4 CHECK TOTAL
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL-MMLU COUNT")
print("=" * 70)

print(
    f"Global-MMLU rows created: "
    f"{len(global_rows)}"
)

print(
    "Expected: 1600 × 3 = 4800"
)


if len(global_rows) == 4800:

    print(
        "OK - Có đúng 4800 rows."
    )

else:

    print(
        "[WARNING] Số rows không đúng 4800."
    )


# ============================================================
# 9.5 CHECK INTERVAL DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL-MMLU INTERVAL SUMMARY")
print("=" * 70)

global_interval_counts = defaultdict(int)

for row in global_rows:

    key = (
        row["interval_id"],
        row["ontology_version"]
    )

    global_interval_counts[key] += 1


for key, count in sorted(
    global_interval_counts.items()
):

    interval_id, ontology_version = key

    print(
        f"interval_id={interval_id} | "
        f"ontology_version={ontology_version} | "
        f"rows={count}"
    )


print("\nExpected:")

print(
    "  Interval 1: 200 × 3 = 600 rows"
)

print(
    "  Interval 2: 400 × 3 = 1200 rows"
)

print(
    "  Interval 3: 500 × 3 = 1500 rows"
)

print(
    "  Interval 4: 500 × 3 = 1500 rows"
)

print(
    "  Total: 1600 × 3 = 4800 rows"
)


# ============================================================
# 10. CHECK GLOBAL-MMLU TOTAL
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL-MMLU COUNT")
print("=" * 70)

print(
    f"Total Global-MMLU rows: "
    f"{len(global_rows)}"
)

print(
    "Expected: 1600 × 3 = 4800"
)


if len(global_rows) == 4800:

    print(
        "OK - Có đúng 4800 Global-MMLU rows."
    )

else:

    print(
        "[WARNING] Số Global-MMLU rows "
        "không đúng 4800."
    )


# ============================================================
# 11. CHECK GLOBAL-MMLU INTERVAL DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL-MMLU INTERVAL SUMMARY")
print("=" * 70)

global_interval_counts = defaultdict(int)

for row in global_rows:

    key = (
        row["interval_id"],
        row["ontology_version"]
    )

    global_interval_counts[key] += 1


for key, count in sorted(
    global_interval_counts.items()
):

    interval_id, ontology_version = key

    print(
        f"interval_id={interval_id} | "
        f"ontology_version={ontology_version} | "
        f"rows={count}"
    )


print("\nExpected:")

print(
    "  Interval 1: 200 × 3 = 600 rows"
)

print(
    "  Interval 2: 400 × 3 = 1200 rows"
)

print(
    "  Interval 3: 500 × 3 = 1500 rows"
)

print(
    "  Interval 4: 500 × 3 = 1500 rows"
)

print(
    "  Total: 1600 × 3 = 4800 rows"
)


# ============================================================
# 12. CHECK DUPLICATE GLOBAL-MMLU RECORDS
#
# Một record được xem là duplicate nếu:
# sample_id + annotator_id giống nhau
# ============================================================

print("\n" + "=" * 70)
print("CHECK GLOBAL-MMLU DUPLICATES")
print("=" * 70)

global_keys = set()
global_duplicates = []

for row in global_rows:

    key = (
        row["item_id"],
        row["annotator_id"]
    )

    if key in global_keys:

        global_duplicates.append(
            key
        )

    global_keys.add(
        key
    )


if global_duplicates:

    print(
        f"[WARNING] Có "
        f"{len(global_duplicates)} "
        f"Global-MMLU duplicate records."
    )

    for key in global_duplicates[:20]:

        print(
            f"  sample_id={key[0]} | "
            f"annotator={key[1]}"
        )

else:

    print(
        "OK - Không có duplicate "
        "sample_id + annotator."
    )


# ============================================================
# 13. CHECK GLOBAL-MMLU AGAINST EXISTING CSV
# ============================================================

print("\n" + "=" * 70)
print(
    "CHECK AGAINST EXISTING annotations_raw.csv"
)
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


already_exists = []

for row in global_rows:

    key = (
        row["item_id"],
        row["annotator_id"]
    )

    if key in existing_keys:

        already_exists.append(
            key
        )


if already_exists:

    print(
        f"[WARNING] Có "
        f"{len(already_exists)} "
        f"Global-MMLU records đã tồn tại "
        f"trong annotations_raw.csv."
    )

    for key in already_exists[:20]:

        print(
            f"  sample_id={key[0]} | "
            f"annotator={key[1]}"
        )

    # Không append duplicate
    global_rows = [
        row
        for row in global_rows
        if (
            row["item_id"],
            row["annotator_id"]
        ) not in existing_keys
    ]

    print(
        f"Global-MMLU rows còn lại sau "
        f"khi loại duplicate: "
        f"{len(global_rows)}"
    )

else:

    print(
        "OK - Không có Global-MMLU record "
        "trùng với CSV hiện tại."
    )


# ============================================================
# 14. COMBINE EXISTING + GLOBAL-MMLU
# ============================================================

print("\n" + "=" * 70)
print("COMBINE DATA")
print("=" * 70)

final_rows = (
    existing_rows
    + global_rows
)


print(
    f"Existing rows       : "
    f"{len(existing_rows)}"
)

print(
    f"Global-MMLU new rows: "
    f"{len(global_rows)}"
)

print(
    f"Final rows          : "
    f"{len(final_rows)}"
)


# ============================================================
# 15. WRITE OUTPUT CSV
# ============================================================

print("\n" + "=" * 70)
print("WRITE OUTPUT CSV")
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

    print(
        "SUCCESS!"
    )

    print(
        f"Output file: {OUTPUT_CSV}"
    )

except PermissionError:

    print(
        "\n[ERROR] Permission denied."
    )

    print(
        f"File {OUTPUT_CSV} đang được mở "
        f"bởi một chương trình khác."
    )

    print(
        "Hãy đóng Excel/LibreOffice rồi chạy lại."
    )

    raise


# ============================================================
# 16. FINAL SOURCE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL SOURCE SUMMARY")
print("=" * 70)

source_counts = defaultdict(int)

for row in final_rows:

    source_counts[
        row["source"]
    ] += 1


for source, count in sorted(
    source_counts.items()
):

    print(
        f"{source}: {count} rows"
    )


# ============================================================
# 17. FINAL EXPECTED SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL EXPECTED SUMMARY")
print("=" * 70)

print(
    "SeaExam:"
)

print(
    "  857 samples × 3 annotators = 2571 rows"
)

print(
    "\nGlobal-MMLU:"
)

print(
    "  1600 samples × 3 annotators = 4800 rows"
)

print(
    "\nCombined:"
)

print(
    "  2571 + 4800 = 7371 rows"
)


# ============================================================
# 18. FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL CHECK")
print("=" * 70)

expected_total = 7371

if len(final_rows) == expected_total:

    print(
        f"OK - Final CSV có đúng "
        f"{expected_total} rows."
    )

else:

    print(
        f"[WARNING] Final CSV có "
        f"{len(final_rows)} rows, "
        f"expected {expected_total}."
    )


print("\nDone.")