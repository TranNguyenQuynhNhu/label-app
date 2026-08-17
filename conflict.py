import json

# ===== CONFIG =====
FILE_1 = "C:\\Users\\Nhu\\my-label-app\\Raw\\Dong_1000_vmlu.json"
FILE_2 = "C:\\Users\\Nhu\\my-label-app\\Raw\\Vy_1000_vmlu.json"
FILE_3 = "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_1000_vmlu.json"

START = 400
N = 500

# ===== LOAD JSON =====
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

data1 = load_json(FILE_1)[START:START + N]
data2 = load_json(FILE_2)[START:START + N]
data3 = load_json(FILE_3)[START:START + N]

# Kiểm tra số lượng sample
if not (len(data1) == len(data2) == len(data3)):
    raise ValueError(
        f"3 file không cùng số sample: "
        f"{len(data1)}, {len(data2)}, {len(data3)}"
    )

# ===== COUNT CONFLICT =====
conflict_count = 0
conflict_indices = []

for i, (s1, s2, s3) in enumerate(zip(data1, data2, data3)):
    labels = [
        s1.get("final_label"),
        s2.get("final_label"),
        s3.get("final_label")
    ]

    # Chỉ cần có ít nhất 2 label khác nhau => conflict
    if len(set(labels)) > 1:
        conflict_count += 1

        # Index thật trong file gốc
        original_index = START + i
        conflict_indices.append(original_index)

        print(f"Sample {original_index}:")
        print(f"  File 1: {labels[0]}")
        print(f"  File 2: {labels[1]}")
        print(f"  File 3: {labels[2]}")
        print()

# ===== RESULT =====
print("=" * 50)
print(f"Samples skipped: {START}")
print(f"Samples evaluated: {len(data1)}")
print(f"Total conflicts: {conflict_count}")
print(f"Conflict rate: {conflict_count / len(data1):.2%}")
print(f"Conflict indices: {conflict_indices}")