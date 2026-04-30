import fs from 'fs';
import path from 'path';

try {
  // 1. Cấu hình tên file cho Global-MMLU
  const inputFileName = 'test.json'; // Đổi tên file đầu vào của bạn ở đây
  const outputDir = path.join('src', 'data');
  const outputFilePath = path.join(outputDir, 'global_mmlu_formatted.json');

  console.log(`🚀 Đang bắt đầu xử lý Global-MMLU từ file ${inputFileName}...`);
  
  if (!fs.existsSync(inputFileName)) {
    throw new Error(`Không tìm thấy file ${inputFileName}!`);
  }

  const rawData = fs.readFileSync(inputFileName, 'utf8');
  let items = [];
  try {
    items = JSON.parse(rawData);
    if (!Array.isArray(items)) items = [items];
  } catch (e) {
    items = rawData.split('\n').filter(line => line.trim() !== '').map(line => JSON.parse(line));
  }

  const formattedData = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    
    // 2. Xử lý Options từ các trường riêng biệt (option_a, option_b, option_c, option_d)
    const optionsArray = [];
    const optionKeys = ['option_a', 'option_b', 'option_c', 'option_d'];
    const alphabet = ['A', 'B', 'C', 'D'];

    optionKeys.forEach((key, index) => {
      if (item[key]) {
        optionsArray.push({
          id: alphabet[index],
          text: item[key]
        });
      }
    });

    // 3. Chuẩn hóa theo Schema yêu cầu cho dự án Global-MMLU
    formattedData.push({
      benchmark_name: "Global-MMLU",
      sample_id: item.sample_id || `global_mmlu_${i}`,
      question: item.question || "",
      options: optionsArray,
      answer: item.answer || "", // Global-MMLU thường lưu sẵn dạng "A", "B", "C"...
      nat_tra_adp_label: null,
      cs_ca_label: null,
      final_label: null,
      annotator: null,
      rationale: null,
      timestamp: null,
      is_annotated: item.is_annotated || false,
      metadata: {
        subject: item.subject || "",
        subject_category: item.subject_category || "",
        cultural_sensitivity_label: item.cultural_sensitivity_label || "-"
      }
    });
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputFilePath, JSON.stringify(formattedData, null, 2), 'utf8');
  console.log(`✅ Thành công! Đã trích xuất ${formattedData.length} câu vào: ${outputFilePath}`);

} catch (error) {
  console.error("❌ Lỗi thực thi:", error.message);
}