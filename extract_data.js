import fs from 'fs';

try {
  console.log("Đang đọc file global_mmlu_vi.json...");
  let rawData = fs.readFileSync('global_mmlu_vi.json', 'utf8');

  // BƯỚC SỬA LỖI: Dọn dẹp dữ liệu, đổi toàn bộ ': NaN' thành ': null'
  rawData = rawData.replace(/:\s*NaN/g, ': null');

  let dataset = JSON.parse(rawData);

  // Xử lý nếu data nằm trong mảng con
  if (!Array.isArray(dataset)) {
    dataset = dataset.data || dataset.rows || Object.values(dataset)[0]; 
  }

  // 1. Nhóm dữ liệu theo subject (môn học)
  const subjectGroup = {};
  
  dataset.forEach(item => {
    // Lấy tên môn học từ sample_id (VD: "abstract_algebra" từ "abstract_algebra/test/0")
    // Nếu không có sample_id, gán tạm vào nhóm 'unknown'
    const subject = item.sample_id ? item.sample_id.split('/')[0] : 'unknown';
    
    if (!subjectGroup[subject]) {
      subjectGroup[subject] = [];
    }
    subjectGroup[subject].push(item);
  });

  // 2. Rút trích 4 câu mỗi môn cho đến khi đủ 228 câu
  const formattedData = [];
  const TARGET_TOTAL = 228;
  const ITEMS_PER_SUBJECT = 4;

  // Lặp qua từng môn học trong object đã nhóm
  for (const subject in subjectGroup) {
    if (formattedData.length >= TARGET_TOTAL) break;

    // Lấy tối đa 4 câu của môn hiện tại
    const itemsToTake = subjectGroup[subject].slice(0, ITEMS_PER_SUBJECT);

   itemsToTake.forEach((item, index) => {
      if (formattedData.length >= TARGET_TOTAL) return;

      // 1. Tách các trường xử lý thủ công ra, gom TẤT CẢ các trường lạ khác vào biến `otherFields`
      const {
        sample_id, question, answer, final_label, choices,
        option_a, option_b, option_c, option_d,
        ...otherFields
      } = item;

      // 2. Push vào mảng
      formattedData.push({
        // Đẩy toàn bộ các trường dư thừa (như subject, required_knowledge...) vào đây
        ...otherFields, 
        
        // Các trường mandatory
        sample_id: sample_id || `${subject}_${index}`,
        question: question || "",
        option_a: option_a || (choices ? choices[0] : ""),
        option_b: option_b || (choices ? choices[1] : ""),
        option_c: option_c || (choices ? choices[2] : ""),
        option_d: option_d || (choices ? choices[3] : ""),
        answer: answer || "",
        final_label: null 
      });
    });
  }

  fs.writeFileSync('src/data.json', JSON.stringify(formattedData, null, 2), 'utf8');
  console.log(`✅ Đã trích xuất thành công ${formattedData.length} câu (tối đa 4 câu mỗi môn) và lưu vào file 'data.json'!`);

} catch (error) {
  console.error("❌ Có lỗi xảy ra:", error.message);
}