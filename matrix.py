import json
import pandas as pd
from sklearn.metrics import confusion_matrix


def load_json_labels(file_path):
    """Reads JSON file and returns a dict mapping sample_id to final_label."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    return {
        item["sample_id"]: item["final_label"]
        for item in data
        if "sample_id" in item and "final_label" in item
    }


def generate_text_confusion_matrix(file_a, file_b):
    # 1. Load data from both files
    labels_a = load_json_labels(file_a)
    labels_b = load_json_labels(file_b)

    # 2. Find matching sample_ids between both annotators
    common_ids = sorted(list(set(labels_a.keys()).intersection(set(labels_b.keys()))))

    if not common_ids:
        print("Error: No matching sample_ids found between the two files!")
        return

    # Align labels based on the common sample_ids
    y_annotator_a = [labels_a[sid] for sid in common_ids]
    y_annotator_b = [labels_b[sid] for sid in common_ids]

    # 3. Get unique sorted list of all labels
    all_classes = sorted(list(set(y_annotator_a + y_annotator_b)))

    # 4. Compute Confusion Matrix
    cm = confusion_matrix(y_annotator_a, y_annotator_b, labels=all_classes)
    cm_df = pd.DataFrame(cm, index=all_classes, columns=all_classes)

    # 5. Print Text-based Confusion Matrix in English
    print("--- CONFUSION MATRIX REPORT ---")
    print("Row: Annotator C  |  Col: Annotator D \n")

    # Format column widths dynamically
    col_width = max(len(str(c)) for c in all_classes) + 6
    header = f"{'C \\ D':<{col_width}}" + "".join(
        f"{col:<{col_width}}" for col in all_classes
    )
    print(header)
    print("-" * len(header))

    for idx, row in cm_df.iterrows():
        row_str = f"{idx:<{col_width}}"
        for val in row:
            row_str += f"{val:<{col_width}}"
        print(row_str)

    # 6. Calculate Exact Match / Agreement Rate
    exact_matches = sum(
        1 for a, b in zip(y_annotator_a, y_annotator_b) if a == b
    )
    agreement_rate = (exact_matches / len(common_ids)) * 100
    print("-" * len(header))
    print(f"Total overlapping samples evaluated: {len(common_ids)}")
    print(
        f"Total agreed samples: {exact_matches}/{len(common_ids)} ({agreement_rate:.2f}%)"
    )


# --- RUN CODE ---
if __name__ == "__main__":
    # Replace 'annotator_A.json' and 'annotator_B.json' with your real file paths
    generate_text_confusion_matrix("Dong_400_labels.json", "vy_400_labels.json")