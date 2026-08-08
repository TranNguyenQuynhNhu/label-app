import json
from collections import Counter

# =========================
# CẤU HÌNH 3 FILE
# =========================
file1 = r"C:\Users\Nhu\my-label-app\Nounk\Dong_900_mmluprox.json"
file2 = r"C:\Users\Nhu\my-label-app\Nounk\Vy_900_mmluprox.json"
file3 = r"C:\Users\Nhu\my-label-app\Nounk\Nhu_900_mmluprox.json"


# =========================
# ĐỌC JSON
# =========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


data1 = load_json(file1)
data2 = load_json(file2)
data3 = load_json(file3)


# =========================
# TẠO DICT THEO sample_id
# =========================
dict1 = {item["sample_id"]: item for item in data1}
dict2 = {item["sample_id"]: item for item in data2}
dict3 = {item["sample_id"]: item for item in data3}


# =========================
# KIỂM TRA
# =========================
all_sample_ids = set(dict1) | set(dict2) | set(dict3)

different_cases = []
missing_cases = []

for sample_id in sorted(all_sample_ids):

    # -------------------------
    # Kiểm tra sample có đủ 3 file
    # -------------------------
    if sample_id not in dict1 or sample_id not in dict2 or sample_id not in dict3:
        missing_cases.append({
            "sample_id": sample_id,
            "file1": sample_id in dict1,
            "file2": sample_id in dict2,
            "file3": sample_id in dict3
        })
        continue

    # -------------------------
    # Lấy final_label
    # -------------------------
    label1 = dict1[sample_id].get("final_label")
    label2 = dict2[sample_id].get("final_label")
    label3 = dict3[sample_id].get("final_label")

    labels = [label1, label2, label3]

    # -------------------------
    # Cả 3 người khác nhau
    # -------------------------
    if len(set(labels)) == 3:
        different_cases.append({
            "sample_id": sample_id,
            "file1": label1,
            "file2": label2,
            "file3": label3
        })


# =========================
# IN KẾT QUẢ
# =========================

print("=" * 70)
print("KẾT QUẢ KIỂM TRA CONSENSUS")
print("=" * 70)

print(f"Tổng sample unique: {len(all_sample_ids)}")
print(f"Sample thiếu ở ít nhất 1 file: {len(missing_cases)}")
print(f"Sample cả 3 người đều khác nhau: {len(different_cases)}")
print()


# =========================
# CÁC CASE CẢ 3 KHÁC NHAU
# =========================

if len(different_cases) == 0:
    print("OK: Không có sample nào mà cả 3 người đều khác nhau.")
    print("=> Tất cả sample đều có ít nhất 2 người có cùng final_label.")
else:
    print("WARNING: Có sample mà cả 3 người đều khác nhau:\n")

    for case in different_cases:
        print(f"sample_id: {case['sample_id']}")
        print(f"  File 1: {case['file1']}")
        print(f"  File 2: {case['file2']}")
        print(f"  File 3: {case['file3']}")
        print("-" * 50)


# =========================
# CÁC SAMPLE BỊ THIẾU
# =========================

if missing_cases:
    print("\n" + "=" * 70)
    print("CÁC SAMPLE KHÔNG CÓ ĐỦ TRONG 3 FILE")
    print("=" * 70)

    for case in missing_cases:
        print(
            f"sample_id: {case['sample_id']} | "
            f"File1: {case['file1']} | "
            f"File2: {case['file2']} | "
            f"File3: {case['file3']}"
        )