import json


def update_nested_labels(input_file, output_file="Ngoc_400_global_fixed.json"):
    print(f"=== PROCESSING FILE: {input_file} ===")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            data = [data]

        updated_count = 0

        for item in data:
            # 1. Truy cập vào trường metadata trước
            metadata = item.get("metadata", {})

            # 2. Kiểm tra trường cultural_sensitivity_label bên trong metadata
            if metadata.get("cultural_sensitivity_label") == "CS":

                # 3. Cập nhật cs_ca_label ở lớp ngoài cùng thành "CS"
                item["cs_ca_label"] = "CS"

                # 4. Cập nhật final_label nếu nó đang là "TRA-CA"
                if item.get("final_label") == "TRA-CA":
                    item["final_label"] = "TRA-CS"

                updated_count += 1

        # Ghi đè hoặc ghi ra file mới tùy bạn (ở đây đang ghi ra file _fixed.json)
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=4)

        print("=== SUCCESS ===")
        print(f"Total samples updated: {updated_count}")
        print(f"Saved updated data to: '{output_file}'")

    except FileNotFoundError:
        print("Error: Input file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")


# --- CHẠY CODE ---
if __name__ == "__main__":
    update_nested_labels(
        input_file="Ngoc_400_global.json", output_file="Ngoc_400_global.json"
    )