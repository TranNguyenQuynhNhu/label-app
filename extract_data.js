import fs from 'fs';

try {
  console.log("Đang đọc file global_mmlu_vi.json...");
  let rawData = fs.readFileSync('global_mmlu_vi.json', 'utf8');

  // BƯỚC SỬA LỖI: Dọn dẹp dữ liệu, đổi toàn bộ ': NaN' thành ': null'
  // để biến nó thành JSON hợp lệ trước khi parse
  rawData = rawData.replace(/:\s*NaN/g, ': null');

  let dataset = JSON.parse(rawData);

  // Xử lý nếu data nằm trong mảng con
  if (!Array.isArray(dataset)) {
    dataset = dataset.data || dataset.rows || Object.values(dataset)[0]; 
  }

  // Lấy 200 câu đầu và format lại cấu trúc
  const formattedData = dataset.slice(0, 200).map((item, index) => {
    return {
      sample_id: item.sample_id || `mmlu_vi_${index}`,
      question: item.question || "",
      option_a: item.option_a || (item.choices ? item.choices[0] : ""),
      option_b: item.option_b || (item.choices ? item.choices[1] : ""),
      option_c: item.option_c || (item.choices ? item.choices[2] : ""),
      option_d: item.option_d || (item.choices ? item.choices[3] : ""),
      answer: item.answer || "",
      final_label: null 
    };
  });

  fs.writeFileSync('data.json', JSON.stringify(formattedData, null, 2), 'utf8');
  console.log("✅ Đã trích xuất thành công 200 câu và lưu vào file 'data.json'!");

} catch (error) {
  console.error("❌ Có lỗi xảy ra:", error.message);
}