import json

# =========================
# File input
# =========================
json_file = r"C:\Users\Nhu\my-label-app\Final\1000_labels_VMLU.json"
jsonl_file = r"C:\Users\Nhu\my-label-app\test.jsonl"

# File output
output_file = r"C:\Users\Nhu\my-label-app\Final\1000_labels_VMLU.json"


# =========================
# 1. Đọc file JSON
# =========================
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Số sample trong JSON: {len(data)}")


# =========================
# 2. Đọc file JSONL
#    Tạo dictionary: id -> category
# =========================
id_to_category = {}

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        item = json.loads(line)

        sample_id = item["id"]
        category = item["category"]

        id_to_category[sample_id] = category

print(f"Số sample trong JSONL: {len(id_to_category)}")


# =========================
# 3. Update category
# =========================
updated_count = 0
not_found = []

for sample in data:
    sample_id = sample.get("sample_id")

    if sample_id in id_to_category:
        new_category = id_to_category[sample_id]

        # Đảm bảo metadata tồn tại
        if "metadata" not in sample:
            sample["metadata"] = {}

        # Update category
        sample["metadata"]["category"] = new_category

        updated_count += 1

    else:
        not_found.append(sample_id)


# =========================
# 4. Lưu file mới
# =========================
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 5. Thống kê
# =========================
print("\n===== KẾT QUẢ =====")
print(f"Tổng sample trong JSON:      {len(data)}")
print(f"Đã update category:          {updated_count}")
print(f"Không tìm thấy trong JSONL:  {len(not_found)}")

if not_found:
    print("\nCác sample không tìm thấy:")
    for sample_id in not_found:
        print(sample_id)

print(f"\nĐã lưu file: {output_file}")