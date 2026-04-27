import fs from 'fs';
import path from 'path';

try {
  // 1. Cập nhật tên file đầu vào cho đúng với tập dữ liệu bạn đang xử lý
  const inputFileName = 'xcopa_final.jsonl'; 
  console.log(`Đang đọc file ${inputFileName}...`);
  
  const rawData = fs.readFileSync(inputFileName, 'utf8');
  const lines = rawData.split('\n').filter(line => line.trim() !== '');

  const formattedData = [];

  for (let i = 0; i < lines.length; i++) {
    try {
      const item = JSON.parse(lines[i]);
      
      const optionsArray = [];
      const choiceLabels = ['A', 'B', 'C', 'D', 'E', 'F']; 
      
      if (item.choices && item.choices.length > 0) {
        item.choices.forEach((choiceText, idx) => {
          optionsArray.push({
            id: choiceLabels[idx],
            text: choiceText
          });
        });
      }

      // 2. Destructuring để lấy 'context' thay vì 'flores_passage'
      const {
        id, 
        question, 
        context, // Trường chứa ngữ cảnh của XCOPA
        choices, 
        answer, 
        metadata: existingMetadata, 
        ...otherFields
      } = item;

      const combinedMetadata = { ...existingMetadata, ...otherFields };

      // 3. Logic gộp: Nếu có context thì gộp, không thì chỉ lấy question
      // Cấu trúc: [Ngữ cảnh] + [Câu hỏi]
      const combinedQuestion = context 
        ? `${context}\n\nCâu hỏi: ${question}` 
        : (question || "");

      formattedData.push({
        benchmark_name: item.source || "XCOPA",
        sample_id: id || `xcopa_${i}`,
        question: combinedQuestion, 
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

  const dir = 'src';
  // Đổi tên file output tương ứng
  const filePath = path.join(dir, 'XCOPAdata.json'); 
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(filePath, JSON.stringify(formattedData, null, 2), 'utf8');
  console.log(`✅ Đã trích xuất thành công ${formattedData.length} câu từ XCOPA!`);

} catch (error) {
  console.error("❌ Có lỗi xảy ra:", error.message);
}