import json

FILE_A = r"C:\Users\Nhu\my-label-app\Raw\Khang_1600_globalmmlu.json"
FILE_B = r"C:\Users\Nhu\my-label-app\Raw\Nhu_1600_globalmmlu.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


data_a = load_json(FILE_A)
data_b = load_json(FILE_B)

# Lấy sample_id của mỗi file
ids_a = {
    sample["sample_id"]
    for sample in data_a
    if "sample_id" in sample
}

ids_b = {
    sample["sample_id"]
    for sample in data_b
    if "sample_id" in sample
}

# Những sample có trong B nhưng không có trong A
missing_in_a = ids_b - ids_a

# Những sample có trong A nhưng không có trong B
extra_in_a = ids_a - ids_b

print("=" * 60)
print(f"File A: {FILE_A}")
print(f"File B: {FILE_B}")
print("=" * 60)

print(f"Số sample trong A        : {len(ids_a)}")
print(f"Số sample trong B        : {len(ids_b)}")
print(f"A thiếu so với B         : {len(missing_in_a)}")
print(f"A có thêm so với B       : {len(extra_in_a)}")
print("=" * 60)


# -----------------------------
# A thiếu những sample nào?
# -----------------------------
if missing_in_a:
    print("\nCác sample A đang thiếu so với B:")

    for sample_id in sorted(missing_in_a):
        print(sample_id)
else:
    print("\nA không thiếu sample nào so với B.")


# -----------------------------
# A có thêm sample nào?
# -----------------------------
if extra_in_a:
    print("\nCác sample A có nhưng B không có:")

    for sample_id in sorted(extra_in_a):
        print(sample_id)
else:
    print("\nA không có sample dư so với B.")