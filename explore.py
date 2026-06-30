from pathlib import Path
import pandas as pd

# ============================
# 1. Đọc toàn bộ file parquet
# ============================

DATA_DIR = "SEA-Instruct-2602-fine-tuned\data"  # đổi thành thư mục chứa file parquet của bạn

files = sorted(Path(DATA_DIR).glob("*.parquet"))

if not files:
    raise FileNotFoundError(f"Không tìm thấy file .parquet trong {DATA_DIR}")

print(f"Found {len(files)} parquet files")

df = pd.concat(
    [pd.read_parquet(f) for f in files],
    ignore_index=True
)

print("=" * 60)
print("DATASET SHAPE")
print("=" * 60)
print(df.shape)

# ============================
# 2. Danh sách cột
# ============================

print("\nCOLUMNS")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

# ============================
# 3. Kiểu dữ liệu
# ============================

print("\nDATA TYPES")
print(df.dtypes)

# ============================
# 4. Missing values
# ============================

missing = pd.DataFrame({
    "missing_count": df.isnull().sum(),
    "missing_percent": (df.isnull().mean()*100).round(2)
})

missing = missing.sort_values(
    by="missing_percent",
    ascending=False
)

print("\nMISSING VALUES")
print(missing)

missing.to_csv(
    "missing_statistics.csv",
    encoding="utf-8-sig"
)

# ============================
# 5. Thông tin tổng quát
# ============================

print("\nFIRST 5 ROWS")
print(df.head())

# ============================
# 6. prompt_primary_domain
# ============================

if "prompt_primary_domain" in df.columns:

    domain_stats = (
        df["prompt_primary_domain"]
        .fillna("NULL")
        .value_counts()
        .reset_index()
    )

    domain_stats.columns = [
        "prompt_primary_domain",
        "count"
    ]

    print("\nPROMPT PRIMARY DOMAIN")
    print(domain_stats)

    domain_stats.to_csv(
        "prompt_primary_domain_distribution.csv",
        index=False,
        encoding="utf-8-sig"
    )

else:
    print("\nprompt_primary_domain NOT FOUND")

# ============================
# 7. Thống kê các cột phân loại
# ============================

categorical_cols = [
    c for c in df.columns
    if df[c].dtype == "object"
]

print("\nCATEGORICAL COLUMNS")
print(categorical_cols)

for col in categorical_cols:

    print("\n" + "=" * 60)
    print(col)
    print("=" * 60)

    print(df[col].value_counts(dropna=False).head(20))

# ============================
# 8. Số lượng giá trị duy nhất
# ============================

unique_df = pd.DataFrame({
    "column": df.columns,
    "unique_values": [df[c].nunique(dropna=False) for c in df.columns]
})

print("\nUNIQUE VALUES")
print(unique_df)

unique_df.to_csv(
    "unique_values.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nDone!")