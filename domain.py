import pandas as pd
from datasets import load_dataset
from huggingface_hub import login

# 1. Tải bộ dữ liệu SEA-Instruct-2602 từ Hugging Face
print("Đang tải dữ liệu...")
dataset = load_dataset("aisingapore/SEA-Instruct-2602", "Vietnamese", split="train")

# 2. Chuyển đổi dataset sang định dạng Pandas DataFrame để dễ thao tác
df = dataset.to_pandas()

# 3. Lọc lấy các giá trị duy nhất trong trường 'prompt_primary_domain'
unique_domains = df['prompt_primary_domain'].dropna().unique()

# 4. Lưu danh sách ra file CSV (có thể mở bằng Excel)
df_domains = pd.DataFrame(unique_domains, columns=['Domain_Name'])
df_domains.to_csv("danh_sach_43_domain.csv", index=False, encoding="utf-8-sig")

print(f"Hoàn tất! Đã xuất danh sách {len(unique_domains)} domain ra file 'danh_sach_43_domain.csv'.")