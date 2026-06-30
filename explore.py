from pathlib import Path
import pandas as pd

DATA_DIR = r"SEA-Instruct-2602-fine-tuned-new\data"

files = sorted(Path(DATA_DIR).glob("*.parquet"))

df = pd.concat(
    [pd.read_parquet(f) for f in files],
    ignore_index=True
)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(df.columns)

# ======================================
# source
# ======================================

print("\nSOURCE DISTRIBUTION")
print(df["source"].value_counts())

df["source"].value_counts().to_csv(
    "source_distribution.csv",
    encoding="utf-8-sig"
)

# ======================================
# number of turns
# ======================================

df["num_turns"] = df["conversations"].apply(len)

print("\nTURN STATISTICS")
print(df["num_turns"].describe())

df["num_turns"].describe().to_csv(
    "turn_statistics.csv",
    encoding="utf-8-sig"
)

# ======================================
# conversation length
# ======================================

def total_characters(conv):
    return sum(len(x["content"]) for x in conv)

df["num_characters"] = df["conversations"].apply(total_characters)

print("\nCHARACTER STATISTICS")
print(df["num_characters"].describe())

df["num_characters"].describe().to_csv(
    "character_statistics.csv",
    encoding="utf-8-sig"
)