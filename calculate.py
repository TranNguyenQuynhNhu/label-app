import json

# =========================
# FILE JSON
# =========================
file_path = r"C:\Users\Nhu\my-label-app\Raw\Khang_857_seaexam.json"


# =========================
# ĐỌC FILE
# =========================
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================
# KIỂM TRA
# =========================
wrong_cases = []

for item in data:
    sample_id = item.get("sample_id")

    nat_tra = item.get("nat_tra_adp_label")
    cs_ca = item.get("cs_ca_label")
    final_label = item.get("final_label")

    # Final label đúng phải được ghép từ 2 field
    expected_final_label = f"{nat_tra}-{cs_ca}"

    if final_label != expected_final_label:
        wrong_cases.append({
            "sample_id": sample_id,
            "nat_tra_adp_label": nat_tra,
            "cs_ca_label": cs_ca,
            "final_label": final_label,
            "expected_final_label": expected_final_label
        })


# =========================
# KẾT QUẢ
# =========================
print("=" * 70)
print("KIỂM TRA final_label")
print("=" * 70)

print(f"Tổng số sample: {len(data)}")
print(f"Số sample sai: {len(wrong_cases)}")
print()

if len(wrong_cases) == 0:
    print("OK: Tất cả final_label đều được cấu thành đúng.")
else:
    print("WARNING: Có sample có final_label không khớp!\n")

    for case in wrong_cases:
        print(f"sample_id: {case['sample_id']}")
        print(f"  nat_tra_adp_label : {case['nat_tra_adp_label']}")
        print(f"  cs_ca_label       : {case['cs_ca_label']}")
        print(f"  final_label       : {case['final_label']}")
        print(f"  expected          : {case['expected_final_label']}")
        print("-" * 70)