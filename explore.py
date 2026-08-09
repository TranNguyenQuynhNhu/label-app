import json
from collections import defaultdict, Counter


# =========================
# CONFIG
# =========================

file_path = r"C:\Users\Nhu\my-label-app\temp.json"


# =========================
# LOAD JSON
# =========================

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================
# THỐNG KÊ
# final_label -> expected
# =========================

stats = defaultdict(Counter)

for item in data:

    final_label = item.get("final_label")
    expected = item.get("expected")

    if final_label is not None and expected is not None:
        stats[final_label][expected] += 1


# =========================
# IN KẾT QUẢ
# =========================

print("=" * 70)
print("FINAL LABEL -> EXPECTED STATISTICS")
print("=" * 70)

for final_label, expected_counts in sorted(stats.items()):

    total = sum(expected_counts.values())

    print()
    print(f"Final label: {final_label}")
    print(f"Total: {total}")
    print("-" * 60)

    for expected, count in expected_counts.most_common():

        percentage = count / total * 100

        print(
            f"  {expected:<25} "
            f"{count:>8} "
            f"({percentage:>6.2f}%)"
        )

print()
print("=" * 70)