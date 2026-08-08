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

# File chứa sample có UNK
UNK_OUTPUT_FILE = "C:\\Users\\Nhu\\my-label-app\\unk.json"

LABEL_FIELDS = [
    "nat_tra_adp_label",
    "cs_ca_label",
    "final_label"
]


def contains_unk(sample):
    """
    Kiểm tra sample có ít nhất một field chứa UNK hay không.
    """
    for field in LABEL_FIELDS:
        value = sample.get(field)

        if value is not None and "UNK" in str(value).upper():
            return True

    return False


def main():

    # ==========================================
    # 1. Load 3 datasets
    # ==========================================

    datasets = []

    for filename in INPUT_FILES:
        with open(filename, "r", encoding="utf-8") as f:
            datasets.append(json.load(f))

    # ==========================================
    # 2. Check số lượng sample
    # ==========================================

    lengths = [len(data) for data in datasets]

    if len(set(lengths)) != 1:
        raise ValueError(
            f"Three files do not have the same number of samples: {lengths}"
        )

    total_samples = lengths[0]

    # ==========================================
    # 3. Containers
    # ==========================================

    # Sample không có UNK ở cả 3 annotator
    valid_indices = []

    # Sample có UNK ở ít nhất 1 annotator
    # Mỗi sample chỉ lấy đúng 1 bản
    unk_samples = []

    # Statistics
    no_unk_count = 0
    one_unk_count = 0
    two_unk_count = 0
    three_unk_count = 0

    # ==========================================
    # 4. Process từng sample
    # ==========================================

    for i in range(total_samples):

        # Kiểm tra UNK của từng annotator
        unk_status = [
            contains_unk(datasets[0][i]),
            contains_unk(datasets[1][i]),
            contains_unk(datasets[2][i])
        ]

        unk_count = sum(unk_status)

        # --------------------------------------
        # Case 0: Không ai có UNK
        # --------------------------------------
        if unk_count == 0:

            # Sample hợp lệ -> lấy ở cả 3 file
            valid_indices.append(i)

            no_unk_count += 1

        # --------------------------------------
        # Case 1: Chỉ 1 annotator có UNK
        # --------------------------------------
        elif unk_count == 1:

            one_unk_count += 1

            # Lấy sample của annotator có UNK
            for annotator_idx in range(3):

                if unk_status[annotator_idx]:

                    unk_samples.append(
                        datasets[annotator_idx][i]
                    )

                    break

        # --------------------------------------
        # Case 2: Có 2 annotator có UNK
        # --------------------------------------
        elif unk_count == 2:

            two_unk_count += 1

            # Chỉ lấy 1 sample trong 2 annotator có UNK
            for annotator_idx in range(3):

                if unk_status[annotator_idx]:

                    unk_samples.append(
                        datasets[annotator_idx][i]
                    )

                    break

        # --------------------------------------
        # Case 3: Cả 3 annotator có UNK
        # --------------------------------------
        elif unk_count == 3:

            three_unk_count += 1

            # Chỉ lấy 1 sample trong 3 annotator
            unk_samples.append(
                datasets[0][i]
            )

    # ==========================================
    # 5. Tạo 3 dataset Nounk
    # ==========================================

    filtered_datasets = [
        [data[i] for i in valid_indices]
        for data in datasets
    ]

    # ==========================================
    # 6. Save 3 file Nounk
    # ==========================================

    for output_file, filtered_data in zip(
        OUTPUT_FILES,
        filtered_datasets
    ):

        with open(output_file, "w", encoding="utf-8") as f:

            json.dump(
                filtered_data,
                f,
                ensure_ascii=False,
                indent=2
            )

    # ==========================================
    # 7. Save unk.json
    # ==========================================

    with open(UNK_OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            unk_samples,
            f,
            ensure_ascii=False,
            indent=2
        )

    # ==========================================
    # 8. Statistics
    # ==========================================

    print("=" * 60)
    print("Filtering completed")
    print("=" * 60)

    print(f"Original samples           : {total_samples}")
    print(f"No UNK (0/3)               : {no_unk_count}")
    print(f"UNK in 1 annotator (1/3)   : {one_unk_count}")
    print(f"UNK in 2 annotators (2/3)  : {two_unk_count}")
    print(f"UNK in 3 annotators (3/3)  : {three_unk_count}")
    print()

    print(f"Samples in Nounk            : {len(valid_indices)}")
    print(f"Samples in unk.json         : {len(unk_samples)}")
    print()

    for filename, filtered_data in zip(
        OUTPUT_FILES,
        filtered_datasets
    ):
        print(f"{filename}: {len(filtered_data)} samples")

    print()
    print(f"UNK output: {UNK_OUTPUT_FILE}")


if __name__ == "__main__":
    main()