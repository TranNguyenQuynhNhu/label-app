import json
import pandas as pd
import numpy as np

# Đường dẫn tới 3 file Nounk của bạn
file_paths = [
    r'C:\Users\Nhu\my-label-app\Nounk\Khang_857_seaexam.json',
    r'C:\Users\Nhu\my-label-app\Nounk\Ngoc_857_seaexam.json',
    r'C:\Users\Nhu\my-label-app\Nounk\Nhu_857_seaexam.json'
]

all_data = []
for path in file_paths:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_data.extend(data)

df = pd.DataFrame(all_data)

# Gom nhóm theo sample_id
grouped = df.groupby('sample_id').agg(
    labels=('final_label', list),
    annotators=('annotator', list)
).reset_index()

# Lọc các mẫu hợp lệ (đúng 3 annotator khác nhau và có đủ 3 nhãn)
valid_samples = []
for _, row in grouped.iterrows():
    if len(set(row['annotators'])) == 3 and len(row['labels']) == 3:
        valid_samples.append(row['labels'])

total_valid = len(valid_samples)
print(f"Tổng số mẫu hợp lệ trong dataset: {total_valid}")

# --- PHÂN CHIA THEO ĐÚNG Ý BẠN ---
# Chọn mode để tính toán: 'first' hoặc 'last'
mode = 'last' # Đổi thành 'first' nếu muốn tính cho phần đầu

if mode == 'first':
    selected_samples = valid_samples[:500]
    print("--- Đang tính cho 500 MẪU ĐẦU TIÊN ---")
else:
    if total_valid >= 1000:
        # Nếu tổng số mẫu >= 1000, lấy đúng 500 mẫu cuối từ dưới đếm lên
        selected_samples = valid_samples[-500:]
        print("--- Đang tính cho 500 MẪU CUỐI CÙNG (đếm ngược từ dưới lên) ---")
    else:
        # Nếu tổng số mẫu từ 501 đến 999, lấy tất cả phần còn lại sau 500 mẫu đầu
        selected_samples = valid_samples[500:]
        print(f"--- Dataset nhỏ hơn 1000 mẫu ({total_valid}), lấy toàn bộ {len(selected_samples)} mẫu còn lại sau mốc 500 ---")

N = len(selected_samples)
n = 3

if N == 0:
    print("Không có mẫu nào để tính toán.")
else:
    # 1. Tính Percent Agreement
    unanimous_count = sum(1 for labels in selected_samples if len(set(labels)) == 1)
    percent_agreement = (unanimous_count / N) * 100

    # 2. Tính Fleiss' Kappa
    P_bar = unanimous_count / N

    flat_labels = [label for labels in selected_samples for label in labels]
    unique_labels, counts = np.unique(flat_labels, return_counts=True)
    
    total_assignments = N * n
    p_j = counts / total_assignments
    Pe_bar = sum(p ** 2 for p in p_j)

    if Pe_bar == 1:
        fleiss_kappa = 1.0
    else:
        fleiss_kappa = (P_bar - Pe_bar) / (1 - Pe_bar)

    print(f"Items evaluated (N)         : {N}")
    print(f"Percent Agreement (%)       : {percent_agreement:.2f}% ({unanimous_count}/{N} mẫu)")
    print(f"Fleiss' Kappa               : {fleiss_kappa:.4f}")