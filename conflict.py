import json
from collections import Counter


# =========================
# CONFIG
# =========================

file_paths = [
    r"C:\Users\Nhu\my-label-app\Conflict data\34_3_globalmmlu",
    r"C:\Users\Nhu\my-label-app\Conflict data\60_3_vmlu.json",
    r"C:\Users\Nhu\my-label-app\Conflict data\106_3_mmluprox.json",
    r"C:\Users\Nhu\my-label-app\Conflict data\231_3_seaexam.json"
]


# =========================
# LOAD VÀ ĐẾM
# =========================

counter = Counter()

total_conflicts = 0

for file_path in file_paths:

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        conflict_type = item.get("conflict_type")

        if conflict_type:
            counter[conflict_type] += 1
            total_conflicts += 1


# =========================
# IN THỐNG KÊ
# =========================

print("=" * 70)
print("CONFLICT TYPE STATISTICS")
print("=" * 70)

print(f"Total conflicts: {total_conflicts}")
print()

print(f"{'Conflict Type':<45} {'Count':>8} {'Percentage':>12}")
print("-" * 70)

for conflict_type, count in counter.most_common():

    percentage = count / total_conflicts * 100

    print(
        f"{conflict_type:<45} "
        f"{count:>8} "
        f"{percentage:>11.2f}%"
    )

print("-" * 70)
print(
    f"{'TOTAL':<45} "
    f"{total_conflicts:>8} "
    f"{100:>11.2f}%"
)