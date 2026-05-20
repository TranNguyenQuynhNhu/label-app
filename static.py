import json
from collections import Counter

# Giả sử dữ liệu của bạn nằm trong file 'data.json' và là một danh sách các câu hỏi
# Nếu file chỉ chứa 1 object như ví dụ của bạn, hãy bọc nó trong dấu [] hoặc điều chỉnh code đọc file.

file_path = "Khang_400_labels_SEAEXAM.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Nếu dữ liệu là một dict đơn lẻ (1 câu hỏi), biến nó thành list để xử lý chung
    if isinstance(data, dict):
        data = [data]

    # Lấy danh sách tất cả các nhãn từ trường 'final_label'
    labels = [item["final_label"] for item in data if "final_label" in item]

    # Đếm số lượng từng nhãn
    total_labels = len(labels)
    label_counts = Counter(labels)

    if total_labels == 0:
        print("Không tìm thấy nhãn nào trong file.")
    else:
        # In kết quả theo định dạng: <tên nhãn> <số lượng nhãn> (phần trăm)
        for label, count in label_counts.items():
            percentage = (count / total_labels) * 100
            print(f"{label} {count} ({percentage:.2f}%)")

except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{file_path}'. Vui lòng kiểm tra lại đường dẫn.")
except json.JSONDecodeError:
    print("Lỗi: File không đúng định dạng JSON.")
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")