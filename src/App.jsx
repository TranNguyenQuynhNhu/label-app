import React, { useState, useEffect } from 'react';
import { Download, ChevronRight, ChevronLeft, Trash2, CheckCircle2, Info, BookOpen, User, AlertCircle, FastForward } from 'lucide-react';

// Đảm bảo bạn đặt file JSON cùng cấp thư mục với App.jsx
import MOCK_DATA from './global_mmlu_vi-ver1.json';

// Danh sách nhãn Nhóm 1: Nguồn Gốc
const NAT_TRA_LABELS = [
  { id: 'NAT', name: 'NAT', base: 'bg-green-100 text-green-800', border: 'border-green-500', ring: 'ring-green-200' },
  { id: 'TRA', name: 'TRA', base: 'bg-blue-100 text-blue-800', border: 'border-blue-500', ring: 'ring-blue-200' },
  { id: 'UNK', name: 'Không xác định', base: 'bg-slate-200 text-slate-800', border: 'border-slate-400', ring: 'ring-slate-300' },
];

// Danh sách nhãn Nhóm 2: Văn Hóa
const CS_CA_LABELS = [
  { id: 'CS', name: 'CS', base: 'bg-purple-100 text-purple-800', border: 'border-purple-500', ring: 'ring-purple-200' },
  { id: 'CA', name: 'CA', base: 'bg-rose-100 text-rose-800', border: 'border-rose-500', ring: 'ring-rose-200' },
  { id: 'UNK', name: 'Không xác định', base: 'bg-slate-200 text-slate-800', border: 'border-slate-400', ring: 'ring-slate-300' },
];

export default function App() {
  const [items, setItems] = useState(MOCK_DATA);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [inputValue, setInputValue] = useState("1"); 
  const [isFinished, setIsFinished] = useState(false);
  // Lấy sẵn tên annotator từ mẫu đầu tiên nếu có, nếu không thì để trống
  const [annotator, setAnnotator] = useState(items[0]?.annotator || "");

  const currentItem = items[currentIndex];
  const progress = Math.round(((currentIndex + 1) / items.length) * 100);
  
  // Đếm số lượng câu đã được gán ĐỦ 2 nhãn
  const labeledCount = items.filter(item => item.nat_tra_label && item.cs_ca_label).length;
  
  // Kiểm tra xem câu hiện tại đã chọn đủ 2 nhãn chưa
  const isCurrentFullyLabeled = Boolean(currentItem?.nat_tra_label && currentItem?.cs_ca_label);

  // Đồng bộ giá trị ô nhập liệu khi chuyển câu bằng nút Next/Prev
  useEffect(() => {
    setInputValue((currentIndex + 1).toString());
  }, [currentIndex]);

  // XỬ LÝ LOGIC KHI GÕ SỐ VÀO Ô
  const handleInputChange = (e) => {
    let val = e.target.value.replace(/[^0-9]/g, ''); // Lọc chỉ cho phép nhập số
    
    if (val !== "") {
      let num = parseInt(val, 10);
      
      // Nếu vượt mốc, tự động ép về câu cuối cùng
      if (num > items.length) {
        num = items.length;
        val = num.toString();
      }
      
      // Tự động nhảy đến câu hợp lệ
      if (num >= 1 && num <= items.length) {
        setCurrentIndex(num - 1);
      }
    }
    
    setInputValue(val);
  };

  // Xử lý khi click ra ngoài (blur)
  const handleInputBlur = () => {
    const num = parseInt(inputValue, 10);
    // Nếu để trống hoặc gõ số 0, tự động trả về số của câu hiện tại
    if (isNaN(num) || num < 1) {
      setInputValue((currentIndex + 1).toString());
    } else {
      setInputValue((currentIndex + 1).toString());
    }
  };

  // Điều hướng cơ bản
  const handleNext = () => {
    if (currentIndex < items.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  // TÌM VÀ NHẢY ĐẾN CÂU CHƯA GÁN NHÃN ĐẦU TIÊN
  const handleJumpToFirstUnlabeled = () => {
    const firstUnlabeledIndex = items.findIndex(item => !(item.nat_tra_label && item.cs_ca_label));
    if (firstUnlabeledIndex !== -1) {
      setCurrentIndex(firstUnlabeledIndex);
    } else {
      alert("Tuyệt vời! Bạn đã gán nhãn hoàn tất toàn bộ dữ liệu.");
    }
  };

  // Xử lý gán nhãn Nhóm 1 (NAT/TRA)
  const handleAssignNatTra = (labelId) => {
    const updatedItems = [...items];
    if (updatedItems[currentIndex].nat_tra_label === labelId) {
      updatedItems[currentIndex].nat_tra_label = null; 
    } else {
      updatedItems[currentIndex].nat_tra_label = labelId; 
    }
    setItems(updatedItems);
  };

  // Xử lý gán nhãn Nhóm 2 (CS/CA)
  const handleAssignCsCa = (labelId) => {
    const updatedItems = [...items];
    if (updatedItems[currentIndex].cs_ca_label === labelId) {
      updatedItems[currentIndex].cs_ca_label = null; 
    } else {
      updatedItems[currentIndex].cs_ca_label = labelId; 
    }
    setItems(updatedItems);
  };

  // Xóa toàn bộ nhãn của câu hiện tại
  const handleClearLabel = () => {
    const updatedItems = [...items];
    updatedItems[currentIndex].nat_tra_label = null;
    updatedItems[currentIndex].cs_ca_label = null;
    setItems(updatedItems);
  };

  // Xuất file JSON
const handleExportJSON = () => {
    if (!annotator.trim()) {
      alert("Vui lòng nhập tên trước khi xuất file!");
      return;
    }

    const exportData = items.map(item => {
      // Kiểm tra xem đã gán đủ 2 nhãn chưa
      const isAnnotated = Boolean(item.nat_tra_label && item.cs_ca_label);
      const finalLabel = isAnnotated ? `${item.nat_tra_label}-${item.cs_ca_label}` : null;

      // 1. XỬ LÝ DYNAMIC OPTIONS (Không fix cứng 4 option A, B, C, D)
      let extractedOptions = item.options;
      if (!extractedOptions) {
        extractedOptions = [];
        // Tự động tìm tất cả các key bắt đầu bằng "option_" (ví dụ option_a, option_e...)
        const optionKeys = Object.keys(item).filter(key => key.startsWith('option_') && item[key] !== null);
        optionKeys.forEach(key => {
          const id = key.replace('option_', '').toUpperCase(); // Chuyển 'option_a' thành 'A'
          extractedOptions.push({ id, text: item[key] });
        });
      }

      // 2. KHAI BÁO CÁC TRƯỜNG MANDATORY (Bắt buộc) & ĐÃ XỬ LÝ
      const mandatoryKeys = [
        'benchmark_name', 'sample_id', 'question', 'options', 'answer',
        'nat_tra_label', 'cs_ca_label', 'final_label', 'annotator', 'timestamp',
        'is_annotated', 'metadata',
        // Khai báo luôn các key 'option_a', 'option_b'... để code biết mà không bốc chúng vào metadata
        ...Object.keys(item).filter(k => k.startsWith('option_'))
      ];

      // 3. LỌC CÁC TRƯỜNG OPTIONAL VÀO OBJECT METADATA
      const dynamicMetadata = { ...(item.metadata || {}) }; // Lấy metadata cũ nếu có
      Object.keys(item).forEach(key => {
        // Nếu key hiện tại KHÔNG nằm trong danh sách mandatory -> nó là optional
        if (!mandatoryKeys.includes(key)) {
          dynamicMetadata[key] = item[key];
        }
      });

      // 4. TRẢ VỀ CẤU TRÚC CHUẨN
      return {
        benchmark_name: item.benchmark_name || "Global-MMLU", 
        sample_id: item.sample_id,
        question: item.question,
        options: item.options, // Lấy trực tiếp mảng options từ dữ liệu gốc
        answer: item.answer,
        nat_tra_label: item.nat_tra_label || null,
        cs_ca_label: item.cs_ca_label || null,
        final_label: finalLabel,
        annotator: annotator.trim(),
        timestamp: isAnnotated ? new Date().toISOString() : null,
        metadata: item.metadata || {}
      };
    });

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `mmlu_annotations_${new Date().getTime()}.json`);
    document.body.appendChild(downloadAnchorNode); 
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm sticky top-0 z-10">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="text-indigo-600" />
            Labeling Studio
          </h1>
          <p className="text-sm text-slate-500 mt-1">Đã đánh nhãn: {labeledCount} / {items.length} mẫu</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center bg-slate-100 rounded-lg px-3 py-2 border border-slate-200 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
            <User size={16} className="text-slate-400 mr-2" />
            <input 
              type="text" 
              placeholder="Tên Annotator..." 
              value={annotator}
              onChange={(e) => setAnnotator(e.target.value)}
              className="bg-transparent border-none outline-none text-sm w-40 text-slate-700 placeholder:text-slate-400"
            />
          </div>
          <button 
            onClick={handleExportJSON}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-sm"
          >
            <Download size={18} />
            Xuất JSON
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col md:flex-row gap-8">
        
        {isFinished ? (
          // Màn hình hoàn tất
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 p-12 flex flex-col items-center justify-center text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle2 size={40} className="text-green-600" />
            </div>
            <h2 className="text-3xl font-bold text-slate-800 mb-3">Hoàn tất quá trình đánh nhãn!</h2>
            <p className="text-lg text-slate-600 mb-8">
              Bạn đã hoàn thành <span className="font-bold text-indigo-600">{labeledCount}/{items.length}</span> mẫu dữ liệu.
            </p>
            
            <div className="flex gap-4">
              <button 
                onClick={() => setIsFinished(false)}
                className="px-6 py-3 rounded-lg border border-slate-300 font-medium text-slate-700 hover:bg-slate-50 transition-colors"
              >
                Quay lại kiểm tra
              </button>
              <button 
                onClick={handleExportJSON}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-sm"
              >
                <Download size={20} />
                Tải file JSON
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Cột trái: Hiển thị câu hỏi MMLU */}
            <div className="flex-1 flex flex-col">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-1 flex-1 flex flex-col overflow-hidden">
                
                {/* Thanh công cụ */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50 rounded-t-lg">
                  <span className="text-sm font-medium text-slate-600 flex items-center gap-2">
                    <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded text-xs font-mono">{currentItem.sample_id}</span>
                    Mẫu #{currentIndex + 1}
                  </span>
                  
                  {isCurrentFullyLabeled && (
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-200 text-slate-700 flex items-center gap-1">
                      Đã gán: {currentItem.nat_tra_label}-{currentItem.cs_ca_label}
                      <button onClick={handleClearLabel} className="hover:text-red-500 ml-1" title="Xóa nhãn">
                        <Trash2 size={12}/>
                      </button>
                    </span>
                  )}
                </div>

                {/* Khu vực đọc (MMLU MCQs) */}
                <div className="flex-1 p-8 bg-slate-50/50 overflow-y-auto">
                  <div className="max-w-3xl mx-auto">
                    {/* Câu hỏi */}
                    <div className="mb-6">
                      <span className="text-xs font-bold text-indigo-500 uppercase tracking-wider mb-2 block">Câu hỏi</span>
                      <h3 className="text-xl font-semibold text-slate-800 leading-relaxed bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                        {currentItem.question}
                      </h3>
                    </div>

                    {/* Các lựa chọn (Được cập nhật để đọc từ mảng options) */}
                    <div className="space-y-3">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Các lựa chọn</span>
                      {currentItem.options && currentItem.options.map((opt) => {
                        const isCorrect = currentItem.answer === opt.id;
                        
                        return (
                          <div 
                            key={opt.id} 
                            className={`p-4 rounded-lg border-2 flex items-start gap-4 ${
                              isCorrect 
                                ? 'border-green-400 bg-green-50 shadow-sm' 
                                : 'border-slate-200 bg-white'
                            }`}
                          >
                            <span className={`font-bold flex-shrink-0 mt-0.5 ${isCorrect ? 'text-green-600' : 'text-slate-400'}`}>
                              {opt.id}.
                            </span>
                            <span className={`leading-relaxed ${isCorrect ? 'text-green-900 font-medium' : 'text-slate-700'}`}>
                              {opt.text}
                            </span>
                            {isCorrect && (
                              <span className="ml-auto flex-shrink-0 text-xs font-bold bg-green-200 text-green-800 px-2 py-1 rounded uppercase">
                                Đáp án
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Thanh điều hướng */}
              <div className="mt-4">
                {!isCurrentFullyLabeled && (
                  <div className="mb-2 text-[13px] text-rose-600 flex items-center gap-1.5 justify-end">
                    <AlertCircle size={14} />
                    <i>Bạn phải chọn đủ 2 nhãn (1 Nguồn gốc, 1 Văn hóa) để đi tiếp.</i>
                  </div>
                )}
                
                <div className="flex justify-between items-center mb-1">
                  <button 
                    onClick={handlePrev} 
                    disabled={currentIndex === 0}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-md bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                  >
                    <ChevronLeft size={16} />
                    Quay lại
                  </button>
                  
                  {/* CỤM ĐIỀU HƯỚNG NHANH TRUNG TÂM */}
                  <div className="flex flex-col items-center gap-1">
                    <div className="flex items-center gap-1.5 bg-white px-2.5 py-1 rounded-md border border-slate-300 shadow-sm">
                      <span className="text-sm text-slate-500 font-medium">Câu</span>
                      <input 
                        type="text"
                        value={inputValue}
                        onChange={handleInputChange}
                        onBlur={handleInputBlur}
                        className="bg-slate-50 border border-slate-200 rounded px-1 py-0.5 text-sm font-semibold text-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-12 text-center"
                        title="Nhập số câu để di chuyển nhanh"
                      />
                      <span className="text-sm text-slate-500 font-medium">/ {items.length}</span>
                    </div>
                    
                    <button 
                      onClick={handleJumpToFirstUnlabeled}
                      className="flex items-center gap-1 text-[11px] font-medium text-indigo-600 hover:text-indigo-800 transition-colors bg-indigo-50 px-2 py-0.5 rounded-full"
                    >
                      <FastForward size={12} />
                      Đến câu chưa gán
                    </button>
                  </div>

                  <button 
                    onClick={() => {
                      if (currentIndex === items.length - 1) {
                        setIsFinished(true);
                      } else {
                        handleNext();
                      }
                    }} 
                    disabled={!isCurrentFullyLabeled}
                    className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-md border transition-colors shadow-sm ${
                      !isCurrentFullyLabeled
                        ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed'
                        : currentIndex === items.length - 1 
                          ? 'bg-indigo-600 text-white hover:bg-indigo-700 border-indigo-600' 
                          : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {currentIndex === items.length - 1 ? 'Hoàn tất' : 'Tiếp theo'}
                    {currentIndex !== items.length - 1 && <ChevronRight size={16} />}
                  </button>
                </div>

                {/* Thanh tiến độ */}
                <div className="w-full bg-slate-200 rounded-full h-1.5 mt-3 overflow-hidden shadow-inner">
                  <div 
                    className="bg-indigo-600 h-1.5 rounded-full transition-all duration-300 ease-out" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Cột phải: Bảng nhãn */}
            <div className="w-full md:w-80 flex flex-col gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 sticky top-24">
                
                {/* Hướng dẫn đánh nhãn mới */}
                <div className="bg-amber-50 p-4 rounded-lg border border-amber-200 mb-5 text-sm text-amber-800 shadow-sm leading-relaxed">
                  <h3 className="font-bold mb-2 flex items-center gap-1.5 text-amber-900"><Info size={16}/> Lưu ý quan trọng</h3>
                  <p className="font-medium text-[13px]">
                    Vui lòng đọc kỹ <strong className="text-amber-900">Guideline</strong> trước khi tiến hành đánh nhãn.<br/><br/>
                    Bạn <strong className="underline">bắt buộc</strong> phải chọn 1 nhãn ở nhóm Nguồn Gốc và 1 nhãn ở nhóm Văn Hóa để có thể sang câu tiếp theo.
                  </p>
                </div>

                <div className="max-h-[60vh] overflow-y-auto pr-2 pb-4 space-y-6">
                  
                  {/* Nhóm 1: Nguồn gốc */}
                  <div>
                    <h2 className="text-sm font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 uppercase tracking-wider">
                      1. Nguồn Gốc (NAT/TRA)
                    </h2>
                    <div className="flex flex-col gap-2">
                      {NAT_TRA_LABELS.map((label) => {
                        const isSelected = currentItem?.nat_tra_label === label.id;
                        return (
                          <button
                            key={label.id}
                            onClick={() => handleAssignNatTra(label.id)}
                            className={`
                              w-full text-left px-4 py-2.5 rounded-lg border-2 transition-all flex justify-between items-center group text-sm
                              ${label.base}
                              ${isSelected 
                                ? `${label.border} ring-2 ${label.ring} shadow-sm font-bold` 
                                : `border-transparent hover:border-slate-300 opacity-70 hover:opacity-100 font-medium`
                              }
                            `}
                          >
                            <span>{label.name}</span>
                            {isSelected && <CheckCircle2 size={16} />}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Nhóm 2: Văn hóa */}
                  <div>
                    <h2 className="text-sm font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 uppercase tracking-wider">
                      2. Văn Hóa (CS/CA)
                    </h2>
                    <div className="flex flex-col gap-2">
                      {CS_CA_LABELS.map((label) => {
                        const isSelected = currentItem?.cs_ca_label === label.id;
                        return (
                          <button
                            key={label.id}
                            onClick={() => handleAssignCsCa(label.id)}
                            className={`
                              w-full text-left px-4 py-2.5 rounded-lg border-2 transition-all flex justify-between items-center group text-sm
                              ${label.base}
                              ${isSelected 
                                ? `${label.border} ring-2 ${label.ring} shadow-sm font-bold` 
                                : `border-transparent hover:border-slate-300 opacity-70 hover:opacity-100 font-medium`
                              }
                            `}
                          >
                            <span>{label.name}</span>
                            {isSelected && <CheckCircle2 size={16} />}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}