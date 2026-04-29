import fs from 'fs';
import path from 'path';

try {
  // 1. Cấu hình tên file cho SeaExam
  const inputFileName = 'test.json'; 
  const outputDir = path.join('src', 'data');
  const outputFilePath = path.join(outputDir, 'seaexam.json');

  console.log(`🚀 Đang bắt đầu xử lý SeaExam từ file ${inputFileName}...`);
  
  if (!fs.existsSync(inputFileName)) {
    throw new Error(`Không tìm thấy file ${inputFileName}! Hãy chắc chắn bạn đã đổi tên file dataset SeaExam thành test.json.`);
  }

  const rawData = fs.readFileSync(inputFileName, 'utf8');
  // Hỗ trợ cả file dạng JSONL (mỗi dòng 1 object) hoặc file mảng JSON chuẩn
  let items = [];
  try {
    items = JSON.parse(rawData);
    if (!Array.isArray(items)) items = [items];
  } catch (e) {
    items = rawData.split('\n').filter(line => line.trim() !== '').map(line => JSON.parse(line));
  }

  const formattedData = [];
  const alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    
    // 2. Xử lý Options từ trường "choices" (Dạng mảng string)
    const optionsArray = [];
    if (item.choices && Array.isArray(item.choices)) {
      item.choices.forEach((choiceText, index) => {
        optionsArray.push({
          id: alphabet[index] || index.toString(),
          text: choiceText
        });
      });
    }

    // 3. Xử lý Answer: Chuyển đổi index (0, 1, 2...) sang nhãn (A, B, C...)
    let finalAnswer = "";
    if (typeof item.answer === 'number') {
      finalAnswer = alphabet[item.answer] || item.answer.toString();
    } else {
      finalAnswer = item.answer || "";
    }

    // 4. Chuẩn hóa theo Schema yêu cầu
    formattedData.push({
      benchmark_name: "SeaExam",
      sample_id: item.id || `seaexam_${i}`,
      question: item.question || "",
      options: optionsArray,
      answer: finalAnswer,
      nat_tra_adp_label: null,
      cs_ca_label: null,
      final_label: null,
      annotator: null,
      rationale: null,
      timestamp: null,
      is_annotated: false,
      metadata: item.metadata || {}
    });
  }

  // Đảm bảo thư mục đầu ra tồn tại
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Ghi file JSON chuẩn
  fs.writeFileSync(outputFilePath, JSON.stringify(formattedData, null, 2), 'utf8');
  console.log(`✅ Thành công! Đã trích xuất ${formattedData.length} câu vào: ${outputFilePath}`);

} catch (error) {
  console.error("❌ Lỗi thực thi:", error.message);
}