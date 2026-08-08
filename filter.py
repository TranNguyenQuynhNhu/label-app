import json


INPUT_FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Khang_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Ngoc_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Raw\\Nhu_857_seaexam.json"
]

OUTPUT_FILES = [
    "C:\\Users\\Nhu\\my-label-app\\Nounk\\Khang_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Nounk\\Ngoc_857_seaexam.json",
    "C:\\Users\\Nhu\\my-label-app\\Nounk\\Nhu_857_seaexam.json"
]

LABEL_FIELDS = [
    "nat_tra_adp_label",
    "cs_ca_label",
    "final_label"
]


def is_valid_sample(sample):
    """
    Sample is valid only if all required fields
    exist and none of them contains 'UNK'.
    """
    for field in LABEL_FIELDS:
        value = sample.get(field)

        if value is None:
            return False

        if "UNK" in str(value).upper():
            return False

    return True


def main():
    # Load all three files
    datasets = []

    for filename in INPUT_FILES:
        with open(filename, "r", encoding="utf-8") as f:
            datasets.append(json.load(f))

    # Check that all files have the same number of samples
    lengths = [len(data) for data in datasets]

    if len(set(lengths)) != 1:
        raise ValueError(
            f"Three files do not have the same number of samples: {lengths}"
        )

    total_samples = lengths[0]

    # Determine which sample indices are valid across ALL 3 annotators
    valid_indices = []

    for i in range(total_samples):
        valid_in_all = all(
            is_valid_sample(datasets[annotator_idx][i])
            for annotator_idx in range(3)
        )

        if valid_in_all:
            valid_indices.append(i)

    # Filter all three datasets using the SAME valid indices
    filtered_datasets = [
        [data[i] for i in valid_indices]
        for data in datasets
    ]

    # Save output files
    for output_file, filtered_data in zip(
        OUTPUT_FILES, filtered_datasets
    ):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                filtered_data,
                f,
                ensure_ascii=False,
                indent=2
            )

    # Statistics
    print("=" * 50)
    print("Filtering completed")
    print("=" * 50)
    print(f"Original samples : {total_samples}")
    print(f"Valid samples    : {len(valid_indices)}")
    print(f"Removed samples  : {total_samples - len(valid_indices)}")
    print()

    for filename, filtered_data in zip(
        OUTPUT_FILES, filtered_datasets
    ):
        print(f"{filename}: {len(filtered_data)} samples")


if __name__ == "__main__":
    main()