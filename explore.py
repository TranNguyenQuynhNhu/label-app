from pathlib import Path
import pandas as pd

DATA_DIR = r"SEA-Instruct-2602-fine-tuned-new\data"

files = sorted(Path(DATA_DIR).glob("*.parquet"))

df = pd.concat(
    [pd.read_parquet(f) for f in files],
    ignore_index=True
)

print("=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== LANGUAGE / SUBSET CHECK ===")

keywords = [
    "lang",
    "language",
    "locale",
    "subset",
    "config",
    "country"
]

found = False

for col in df.columns:
    if any(k in col.lower() for k in keywords):
        found = True
        print(f"\nColumn: {col}")
        print(df[col].value_counts(dropna=False))

if not found:
    print("Không tìm thấy cột nào liên quan đến ngôn ngữ hoặc subset.")
    print("Dataset này nhiều khả năng chỉ chứa một subset duy nhất.")