import pandas as pd

df = pd.read_csv("summary_by_cs_ca_label.csv")

# Xác định các nhóm CS
cs_labels = ["CS-E", "CS-H", "CS-L", "CS-P"]

# Lấy tất cả CS
cs_df = df[df["cs_ca_label"].isin(cs_labels)]

# Tổng số sample của CS
cs_samples = cs_df["samples"].sum()

# Tính weighted average cho các metric
cs_accuracy = (
    (cs_df["accuracy"] * cs_df["samples"]).sum()
    / cs_samples
)

cs_macro_f1 = (
    (cs_df["macro_f1"] * cs_df["samples"]).sum()
    / cs_samples
)

cs_parse_accuracy = (
    (cs_df["parse_accuracy"] * cs_df["samples"]).sum()
    / cs_samples
)

cs_invalid_rate = (
    (cs_df["invalid_rate"] * cs_df["samples"]).sum()
    / cs_samples
)

# Tạo dòng CS
cs_row = pd.DataFrame([{
    "cs_ca_label": "CS",
    "samples": cs_samples,
    "accuracy": cs_accuracy,
    "macro_f1": cs_macro_f1,
    "parse_accuracy": cs_parse_accuracy,
    "invalid_rate": cs_invalid_rate
}])

print(cs_row)