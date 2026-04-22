import fs from 'fs';
import path from 'path';

try {
  console.log("Đang đọc file belebele_final.jsonl...");
  
  // Đọc toàn bộ nội dung file dưới dạng text
  const rawData = fs.readFileSync('belebele_final.jsonl', 'utf8');

  // Tách text thành mảng các dòng, loại bỏ các dòng trống
  const lines = rawData.split('\n').filter(line => line.trim() !== '');

  const formattedData = [];
  const TARGET_TOTAL = 500;

  // Lặp qua từng dòng, parse thành JSON và format
  for (let i = 0; i < lines.length; i++) {
    if (formattedData.length >= TARGET_TOTAL) break;

    try {
      const item = JSON.parse(lines[i]);
      
      // Xử lý mảng choices thành cấu trúc [{"id": "A", "text": "..."}, ...]
      const optionsArray = [];
      const choiceLabels = ['A', 'B', 'C', 'D', 'E', 'F']; 
      
      if (item.choices && item.choices.length > 0) {
        item.choices.forEach((choiceText, idx) => {
          optionsArray.push({
            id: choiceLabels[idx] || String.fromCharCode(65 + idx),
            text: choiceText
          });
        });
      }

      // Tách thêm trường flores_passage ra
      const {
        id, question, flores_passage, choices, answer, metadata: existingMetadata, ...otherFields
      } = item;

      // Hợp nhất metadata hiện có với các trường thừa khác
      const combinedMetadata = { ...existingMetadata, ...otherFields };

      // Gộp flores_passage và question lại với nhau
      const combinedQuestion = flores_passage 
        ? `${flores_passage}\n\nCâu hỏi: ${question}` 
        : (question || "");

      // Push cấu trúc chuẩn theo đúng Schema
      formattedData.push({
        benchmark_name: item.source || "Belebele",
        sample_id: id || `belebele_${i}`,
        question: combinedQuestion, // Đã thay bằng câu hỏi gộp đoạn văn
        options: optionsArray,
        answer: answer || "",
        nat_tra_adp_label: null,
        cs_ca_label: null,
        final_label: null,
        annotator: null,
        rationale: null,
        timestamp: null,
        is_annotated: false,
        metadata: combinedMetadata
      });
    } catch (parseError) {
      console.warn(`Bỏ qua dòng ${i + 1} vì lỗi:`, parseError.message);
    }
  }

  // Đảm bảo thư mục src tồn tại
  const dir = 'src';
  const filePath = path.join(dir, 'data.json');
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // Lưu file
  fs.writeFileSync(filePath, JSON.stringify(formattedData, null, 2), 'utf8');
  console.log(`✅ Đã trích xuất thành công ${formattedData.length} câu từ Belebele và lưu vào file '${filePath}'!`);

} catch (error) {
  console.error("❌ Có lỗi xảy ra:", error.message);
}