import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Thay bằng tên/đường dẫn thật của 3 file JSON
FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Khang_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Ngoc_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_857_seaexam.json",
]

OUTPUT_FILE = "annotations_raw.csv"


# ============================================================
# 2. EXPECTED LABELS
# ============================================================

VALID_CS_LABELS = {
    "CA",
    "CS-L",
    "CS-E",
    "CS-P",
    "CS-H",
    "UNK",
}

VALID_TO_LABELS = {
    "NAT",
    "TRA",
    "ADP",
    "UNK",
}


# ============================================================
# 3. LOAD JSON
# ============================================================

def load_json(path):
    """
    Load JSON file.

    Supports:
        - [...]
        - {"data": [...]}
        - {"samples": [...]}
        - {"annotations": [...]}
        - {"items": [...]}
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # JSON là list
    if isinstance(data, list):
        return data

    # JSON là dict chứa list
    if isinstance(data, dict):

        possible_keys = [
            "data",
            "samples",
            "annotations",
            "items"
        ]

        for key in possible_keys:

            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError(
        f"Không nhận diện được format JSON của file: {path}"
    )


# ============================================================
# 4. NORMALIZE TIMESTAMP
# ============================================================

def normalize_timestamp(timestamp):
    """
    Convert timestamp to ISO 8601 UTC.

    Example:

        Input:
        2026-06-14T07:23:17.372Z

        Output:
        2026-06-14T07:23:17.372Z
    """

    if timestamp is None:
        return ""

    timestamp = str(timestamp).strip()

    if timestamp == "":
        return ""

    try:

        # Convert trailing Z -> +00:00
        timestamp_for_parse = timestamp.replace(
            "Z",
            "+00:00"
        )

        dt = datetime.fromisoformat(
            timestamp_for_parse
        )

        # Nếu không có timezone
        if dt.tzinfo is None:

            print(
                f"[WARNING] Timestamp không có timezone, "
                f"giả sử UTC: {timestamp}"
            )

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        # Convert về UTC
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

        print(f"         Error: {e}")

        # Giữ nguyên nếu không parse được
        return timestamp


# ============================================================
# 5. SEAEXAM INTERVAL + ONTOLOGY VERSION
# ============================================================

def get_interval_and_ontology(
    source,
    position
):
    """
    SeaExam:

        1-200   -> interval 1 -> v1
        201-600 -> interval 2 -> v2
        601-857 -> interval 3 -> v3

    position bắt đầu từ 1.
    """

    source_normalized = str(
        source
    ).strip().lower()

    if source_normalized != "seaexam":
        return "", ""

    if 1 <= position <= 200:

        return "1", "v1"

    elif 201 <= position <= 600:

        return "2", "v2"

    elif 601 <= position <= 857:

        return "3", "v3"

    else:

        print(
            f"[WARNING] SeaExam position "
            f"{position} nằm ngoài 1-857."
        )

        return "", ""


# ============================================================
# 6. LOAD ALL THREE FILES
# ============================================================

print("=" * 70)
print("LOADING ANNOTATION FILES")
print("=" * 70)

all_records = []

file_data = {}

for file_path in FILES:

    data = load_json(file_path)

    file_data[file_path] = data

    print(
        f"{file_path}: {len(data)} samples"
    )

    for sample in data:

        all_records.append({
            "file": file_path,
            "sample": sample
        })


# ============================================================
# 7. CHECK DUPLICATE SAMPLE_ID INSIDE EACH FILE
# ============================================================

print("\n" + "=" * 70)
print("CHECK DUPLICATE SAMPLE_ID WITHIN EACH FILE")
print("=" * 70)

for file_path, data in file_data.items():

    seen_ids = set()
    duplicates = []

    for sample in data:

        sample_id = sample.get(
            "sample_id"
        )

        if sample_id is None:
            continue

        if sample_id in seen_ids:

            duplicates.append(
                sample_id
            )

        seen_ids.add(
            sample_id
        )

    if duplicates:

        print(
            f"[WARNING] {file_path} có "
            f"{len(duplicates)} duplicate sample_id."
        )

        for sample_id in duplicates[:20]:

            print(
                f"  - {sample_id}"
            )

    else:

        print(
            f"OK: {file_path} không có duplicate."
        )


# ============================================================
# 8. BUILD:
#    sample_id -> annotator -> sample
# ============================================================

sample_map = defaultdict(dict)

for record in all_records:

    sample = record["sample"]

    sample_id = sample.get(
        "sample_id"
    )

    annotator = sample.get(
        "annotator"
    )

    if not sample_id:

        print(
            f"[WARNING] Sample không có sample_id "
            f"trong {record['file']}"
        )

        continue

    if not annotator:

        print(
            f"[WARNING] sample_id={sample_id} "
            f"không có annotator "
            f"trong {record['file']}"
        )

        continue

    if annotator in sample_map[sample_id]:

        print(
            f"[WARNING] Duplicate annotation:"
        )

        print(
            f"  sample_id = {sample_id}"
        )

        print(
            f"  annotator = {annotator}"
        )

    sample_map[
        sample_id
    ][annotator] = sample


# ============================================================
# 9. FIND ALL ANNOTATORS
# ============================================================

all_annotators = set()

for annotations in sample_map.values():

    all_annotators.update(
        annotations.keys()
    )

print("\n" + "=" * 70)
print("ANNOTATORS FOUND")
print("=" * 70)

print(
    sorted(all_annotators)
)


# ============================================================
# 10. CHECK MISSING ANNOTATORS
# ============================================================

print("\n" + "=" * 70)
print("CHECK MISSING ANNOTATORS")
print("=" * 70)

missing_samples = []

for sample_id, annotations in sample_map.items():

    missing = (
        all_annotators
        - set(annotations.keys())
    )

    if missing:

        missing_samples.append({
            "sample_id": sample_id,
            "missing": sorted(missing)
        })


if missing_samples:

    print(
        f"[WARNING] Có "
        f"{len(missing_samples)} sample "
        f"không có đủ annotator."
    )

    for item in missing_samples[:50]:

        print(
            f"  {item['sample_id']} "
            f"-> missing: {item['missing']}"
        )

else:

    print(
        "OK - Tất cả sample đều có đủ annotator."
    )


# ============================================================
# 11. CHECK TIMESTAMP DUPLICATION
#     ACROSS ANNOTATORS OF THE SAME SAMPLE
# ============================================================

print("\n" + "=" * 70)
print(
    "CHECK SAME TIMESTAMP ACROSS ANNOTATORS"
)
print("=" * 70)

duplicate_cross_annotator = []

for sample_id, annotations in sample_map.items():

    # Cần ít nhất 2 annotator mới có thể so sánh
    if len(annotations) < 2:
        continue

    timestamp_groups = defaultdict(list)

    for annotator, sample in annotations.items():

        timestamp = sample.get(
            "timestamp",
            ""
        )

        if not timestamp:
            continue

        normalized_timestamp = (
            normalize_timestamp(timestamp)
        )

        timestamp_groups[
            normalized_timestamp
        ].append({
            "annotator": annotator,
            "timestamp": normalized_timestamp
        })

    # Timestamp xuất hiện >= 2 annotator
    for timestamp, records in timestamp_groups.items():

        if len(records) >= 2:

            duplicate_cross_annotator.append({
                "sample_id": sample_id,
                "timestamp": timestamp,
                "annotators": records
            })


if duplicate_cross_annotator:

    print(
        f"[WARNING] Phát hiện "
        f"{len(duplicate_cross_annotator)} sample "
        f"có timestamp giống nhau giữa "
        f"các annotator."
    )

    for item in duplicate_cross_annotator:

        print("\n" + "-" * 50)

        print(
            f"sample_id: {item['sample_id']}"
        )

        print(
            f"timestamp: {item['timestamp']}"
        )

        for record in item["annotators"]:

            print(
                f"  annotator={record['annotator']} "
                f"| timestamp={record['timestamp']}"
            )

else:

    print(
        "OK - Không có sample nào có timestamp "
        "giống nhau giữa các annotator."
    )


# ============================================================
# 12. CHECK INVALID / MISSING LABELS
# ============================================================

print("\n" + "=" * 70)
print("CHECK LABELS")
print("=" * 70)

invalid_cs = []
invalid_to = []

for sample_id, annotations in sample_map.items():

    for annotator, sample in annotations.items():

        cs_label = sample.get(
            "cs_ca_label",
            ""
        )

        to_label = sample.get(
            "nat_tra_adp_label",
            ""
        )

        if cs_label not in VALID_CS_LABELS:

            invalid_cs.append({
                "sample_id": sample_id,
                "annotator": annotator,
                "value": cs_label
            })

        if to_label not in VALID_TO_LABELS:

            invalid_to.append({
                "sample_id": sample_id,
                "annotator": annotator,
                "value": to_label
            })


if invalid_cs:

    print(
        f"[WARNING] Có "
        f"{len(invalid_cs)} cs_label không hợp lệ."
    )

    for item in invalid_cs[:20]:

        print(
            f"  {item['sample_id']} | "
            f"{item['annotator']} | "
            f"{item['value']}"
        )

else:

    print(
        "OK - Tất cả cs_label hợp lệ."
    )


if invalid_to:

    print(
        f"[WARNING] Có "
        f"{len(invalid_to)} to_label không hợp lệ."
    )

    for item in invalid_to[:20]:

        print(
            f"  {item['sample_id']} | "
            f"{item['annotator']} | "
            f"{item['value']}"
        )

else:

    print(
        "OK - Tất cả to_label hợp lệ."
    )


# ============================================================
# 13. DETERMINE SEAEXAM ORDER
# ============================================================

print("\n" + "=" * 70)
print("DETERMINE SEAEXAM ORDER")
print("=" * 70)

# Lấy thứ tự SeaExam từ file đầu tiên
first_file = FILES[0]

seaexam_order = []

for sample in file_data[first_file]:

    source = sample.get(
        "benchmark_name",
        ""
    )

    if str(source).strip().lower() == "seaexam":

        sample_id = sample.get(
            "sample_id"
        )

        if sample_id:

            seaexam_order.append(
                sample_id
            )


print(
    f"SeaExam samples found: "
    f"{len(seaexam_order)}"
)

if len(seaexam_order) != 857:

    print(
        "[WARNING] Không tìm thấy đúng "
        "857 SeaExam samples."
    )

else:

    print(
        "OK - Có đúng 857 SeaExam samples."
    )


# ============================================================
# 14. CHECK SEAEXAM DUPLICATE ORDER
# ============================================================

seaexam_duplicates = []

seen_seaexam = set()

for sample_id in seaexam_order:

    if sample_id in seen_seaexam:

        seaexam_duplicates.append(
            sample_id
        )

    seen_seaexam.add(
        sample_id
    )


if seaexam_duplicates:

    print(
        f"[WARNING] SeaExam có "
        f"{len(seaexam_duplicates)} duplicate sample_id "
        f"trong thứ tự."
    )

else:

    print(
        "OK - Không có duplicate trong "
        "SeaExam order."
    )


# ============================================================
# 15. CREATE OUTPUT ROWS
# ============================================================

output_rows = []


# ============================================================
# 15A. PROCESS SEAEXAM
# ============================================================

for position, sample_id in enumerate(
    seaexam_order,
    start=1
):

    annotations = sample_map.get(
        sample_id,
        {}
    )

    interval_id, ontology_version = (
        get_interval_and_ontology(
            "SeaExam",
            position
        )
    )

    for annotator, sample in annotations.items():

        raw_timestamp = sample.get(
            "timestamp",
            ""
        )

        annotated_at = normalize_timestamp(
            raw_timestamp
        )

        output_rows.append({

            "item_id": sample_id,

            "source": sample.get(
                "benchmark_name",
                ""
            ),

            "annotator_id": annotator,

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

            # Chưa có dữ liệu
            "is_reevaluation": "",

            "triggered_refinement": ""
        })


# ============================================================
# 15B. PROCESS OTHER DATASETS
# ============================================================

for sample_id, annotations in sample_map.items():

    # Xác định source
    source = ""

    if annotations:

        first_sample = next(
            iter(annotations.values())
        )

        source = first_sample.get(
            "benchmark_name",
            ""
        )

    # SeaExam đã xử lý ở trên
    if str(source).strip().lower() == "seaexam":

        continue

    # Dataset khác
    for annotator, sample in annotations.items():

        raw_timestamp = sample.get(
            "timestamp",
            ""
        )

        annotated_at = normalize_timestamp(
            raw_timestamp
        )

        output_rows.append({

            "item_id": sample_id,

            "source": sample.get(
                "benchmark_name",
                ""
            ),

            "annotator_id": annotator,

            "cs_label": sample.get(
                "cs_ca_label",
                ""
            ),

            "to_label": sample.get(
                "nat_tra_adp_label",
                ""
            ),

            "annotated_at": annotated_at,

            # Chưa có quy tắc cho dataset khác
            "interval_id": "",

            "ontology_version": "",

            # Chưa có dữ liệu
            "is_reevaluation": "",

            "triggered_refinement": ""
        })


# ============================================================
# 16. DEFINE CSV COLUMNS
# ============================================================

columns = [
    "item_id",
    "source",
    "annotator_id",
    "cs_label",
    "to_label",
    "annotated_at",
    "interval_id",
    "ontology_version",
    "is_reevaluation",
    "triggered_refinement"
]


# ============================================================
# 17. WRITE CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=columns
    )

    writer.writeheader()

    writer.writerows(
        output_rows
    )


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINISHED")
print("=" * 70)

print(
    f"Output: {OUTPUT_FILE}"
)

print(
    f"Total rows: {len(output_rows)}"
)

print(
    f"Unique samples: {len(sample_map)}"
)

print("\nCSV columns:")

for column in columns:

    print(
        f"  - {column}"
    )


# ============================================================
# 19. SEAEXAM SUMMARY
# ============================================================

seaexam_rows = [
    row
    for row in output_rows
    if str(row["source"]).strip().lower()
    == "seaexam"
]

print("\n" + "=" * 70)
print("SEAEXAM SUMMARY")
print("=" * 70)

print(
    f"SeaExam rows: {len(seaexam_rows)}"
)

print(
    "Expected:"
)

print(
    "  857 samples × 3 annotators = 2571 rows"
)

print(
    "\nInterval mapping:"
)

print(
    "  Position   1-200  → interval_id=1, ontology_version=v1"
)

print(
    "  Position 201-600  → interval_id=2, ontology_version=v2"
)

print(
    "  Position 601-857  → interval_id=3, ontology_version=v3"
)


# ============================================================
# 20. FINAL WARNING SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("WARNING SUMMARY")
print("=" * 70)

print(
    f"Duplicate sample_id within files: "
    f"CHECKED"
)

print(
    f"Samples missing annotators: "
    f"{len(missing_samples)}"
)

print(
    f"Same timestamp across annotators: "
    f"{len(duplicate_cross_annotator)} samples"
)

print(
    f"Invalid cs_label: "
    f"{len(invalid_cs)}"
)

print(
    f"Invalid to_label: "
    f"{len(invalid_to)}"
)

print("\nDone.")