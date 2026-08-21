import pandas as pd

df = pd.read_csv("summary_metrics.csv")

# Tổng số samples
total_samples = df["samples"].sum()

# Overall accuracy: weighted theo số sample
overall_accuracy = (
    (df["accuracy"] * df["samples"]).sum()
    / total_samples
)

# Overall parse accuracy
overall_parse_accuracy = (
    (df["parse_accuracy"] * df["samples"]).sum()
    / total_samples
)

# Overall invalid rate
overall_invalid_rate = (
    (df["invalid_rate"] * df["samples"]).sum()
    / total_samples
)

# Macro-F1:
# Không nên weighted-average nếu bạn muốn macro-F1 đúng nghĩa trên
# toàn bộ sample; cần prediction/label từng sample để tính lại.
# Nếu chỉ muốn weighted average của 4 giá trị macro-F1:
overall_macro_f1_weighted = (
    (df["macro_f1"] * df["samples"]).sum()
    / total_samples
)

print("Overall metrics:")
print(f"Samples:           {total_samples}")
print(f"Accuracy:          {overall_accuracy:.6f}")
print(f"Accuracy (%):      {overall_accuracy * 100:.2f}%")
print(f"Macro-F1 weighted: {overall_macro_f1_weighted:.6f}")
print(f"Parse Accuracy:    {overall_parse_accuracy:.6f}")
print(f"Invalid Rate:      {overall_invalid_rate:.6f}")