import json

# Đọc 2 file annotation
with open("Khang_400_labels_SEAEXAM.json", "r", encoding="utf-8") as f:
    data1 = json.load(f)

with open("Ngoc_400_sea.json", "r", encoding="utf-8") as f:
    data2 = json.load(f)

# Map sample_id -> sample
map1 = {sample["sample_id"]: sample for sample in data1}
map2 = {sample["sample_id"]: sample for sample in data2}

conflicts = []

# Tìm các sample có conflict
for sample_id in map1:
    if sample_id in map2:
        label1 = map1[sample_id]["final_label"]
        label2 = map2[sample_id]["final_label"]

        if label1 != label2:
            conflicts.append({
                "sample_id": sample_id,
                "question": map1[sample_id]["question"],

                "annotator_1": map1[sample_id]["annotator"],
                "label_1": label1,

                "annotator_2": map2[sample_id]["annotator"],
                "label_2": label2,

                "sample_1": map1[sample_id],
                "sample_2": map2[sample_id]
            })

# Lưu kết quả conflict
with open("conflicts.json", "w", encoding="utf-8") as f:
    json.dump(conflicts, f, ensure_ascii=False, indent=2)

print(f"Found {len(conflicts)} conflict samples.")