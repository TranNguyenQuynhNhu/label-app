import React, { useState } from 'react';
import { Download, ChevronRight, ChevronLeft, Trash2, CheckCircle2, Info, BookOpen, User } from 'lucide-react';

import MOCK_DATA from './data.json';

// Danh sách nhãn mặc định
const DEFAULT_LABELS = [
  { id: 'NAT-CS', name: 'NAT-CS (Gốc VN - Cần VH)', base: 'bg-green-100 text-green-800', border: 'border-green-500', ring: 'ring-green-200' },
  { id: 'NAT-CA', name: 'NAT-CA (Gốc VN - Chung chung)', base: 'bg-yellow-100 text-yellow-800', border: 'border-yellow-500', ring: 'ring-yellow-200' },
  { id: 'TRA-CS', name: 'TRA-CS (Bản dịch - Cần VH)', base: 'bg-purple-100 text-purple-800', border: 'border-purple-500', ring: 'ring-purple-200' },
  { id: 'TRA-CA', name: 'TRA-CA (Bản dịch - Chung chung)', base: 'bg-rose-100 text-rose-800', border: 'border-rose-500', ring: 'ring-rose-200' },
];

export default function App() {
  const [items, setItems] = useState(MOCK_DATA);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [labels] = useState(DEFAULT_LABELS);
  const [isFinished, setIsFinished] = useState(false);
  const [annotator, setAnnotator] = useState("");

  const currentItem = items[currentIndex];
  const progress = Math.round(((currentIndex + 1) / items.length) * 100);
  const labeledCount = items.filter(item => item.final_label !== null).length;

  // Điều hướng
  const handleNext = () => {
    if (currentIndex < items.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  // Xử lý gán nhãn
  const handleAssignLabel = (labelId) => {
    const updatedItems = [...items];
    if (updatedItems[currentIndex].final_label === labelId) {
      updatedItems[currentIndex].final_label = null; // Bỏ chọn
    } else {
      updatedItems[currentIndex].final_label = labelId; // Gán nhãn mới
    }
    setItems(updatedItems);
  };

  // Xử lý xóa nhãn
  const handleClearLabel = () => {
    const updatedItems = [...items];
    updatedItems[currentIndex].final_label = null;
    setItems(updatedItems);
  };

  // Xuất file JSON theo đúng định dạng Schema
  const handleExportJSON = () => {
    if (!annotator.trim()) {
      alert("Vui lòng nhập tên Người đánh nhãn (Annotator) trước khi xuất file!");
      return;
    }

    const exportData = items.map(item => {
      // Tách nhãn NAT_TRA và CS_CA từ final_label
      let nat_tra = "";
      let cs_ca = "";
      if (item.final_label) {
        const parts = item.final_label.split('-');
        if (parts.length === 2) {
          nat_tra = parts[0];
          cs_ca = parts[1];
        }
      }

      return {
        sample_id: item.sample_id,
        question: item.question,
        option_a: item.option_a,
        option_b: item.option_b,
        option_c: item.option_c,
        option_d: item.option_d,
        answer: item.answer,
        nat_tra_label: nat_tra || null,
        cs_ca_label: cs_ca || null,
        final_label: item.final_label || null,
        annotator: annotator.trim(),
        timestamp: item.final_label ? new Date().toISOString() : null
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
            MMLU Labeling Studio
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
              Bạn đã đánh nhãn <span className="font-bold text-indigo-600">{labeledCount}/{items.length}</span> mẫu dữ liệu.
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
                  {currentItem.final_label && (
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-200 text-slate-700 flex items-center gap-1">
                      Đã đánh nhãn
                      <button onClick={handleClearLabel} className="hover:text-red-500 ml-1"><Trash2 size={12}/></button>
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

                    {/* Các lựa chọn */}
                    <div className="space-y-3">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Các lựa chọn</span>
                      {['A', 'B', 'C', 'D'].map((opt) => {
                        const optionKey = `option_${opt.toLowerCase()}`;
                        const isCorrect = currentItem.answer === opt;
                        
                        return (
                          <div 
                            key={opt} 
                            className={`p-4 rounded-lg border-2 flex items-start gap-4 ${
                              isCorrect 
                                ? 'border-green-400 bg-green-50 shadow-sm' 
                                : 'border-slate-200 bg-white'
                            }`}
                          >
                            <span className={`font-bold flex-shrink-0 mt-0.5 ${isCorrect ? 'text-green-600' : 'text-slate-400'}`}>
                              {opt}.
                            </span>
                            <span className={`leading-relaxed ${isCorrect ? 'text-green-900 font-medium' : 'text-slate-700'}`}>
                              {currentItem[optionKey]}
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
              <div className="mt-6">
                <div className="flex justify-between items-center mb-2">
                  <button 
                    onClick={handlePrev} 
                    disabled={currentIndex === 0}
                    className="flex items-center gap-1 px-4 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft size={18} />
                    Quay lại
                  </button>
                  <span className="text-sm text-slate-500 font-medium">
                    {currentIndex + 1} / {items.length}
                  </span>
                  <button 
                    onClick={() => {
                      if (currentIndex === items.length - 1) {
                        setIsFinished(true);
                      } else {
                        handleNext();
                      }
                    }} 
                    className={`flex items-center gap-1 px-4 py-2 rounded-lg border transition-colors ${
                      currentIndex === items.length - 1 
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700 border-indigo-600 shadow-sm' 
                        : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {currentIndex === items.length - 1 ? 'Hoàn tất' : 'Tiếp theo'}
                    {currentIndex !== items.length - 1 && <ChevronRight size={18} />}
                  </button>
                </div>
                {/* Thanh tiến độ */}
                <div className="w-full bg-slate-200 rounded-full h-2 mt-4 overflow-hidden">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300 ease-out" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Cột phải: Bảng nhãn */}
            <div className="w-full md:w-80 flex flex-col gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 sticky top-24">
                
                {/* Hướng dẫn đánh nhãn */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 mb-5 text-sm text-blue-800 shadow-sm leading-relaxed">
                  <h3 className="font-bold mb-2 flex items-center gap-1.5 text-blue-900"><Info size={16}/> Hướng dẫn đánh nhãn</h3>
                  <ul className="space-y-1.5 list-disc pl-5 text-[13px]">
                    <li><strong>NAT:</strong> Gốc tiếng Việt, không dịch.</li>
                    <li><strong>TRA:</strong> Dịch từ ngôn ngữ khác.</li>
                    <li><strong>CS:</strong> Cần kiến thức VH/Địa lý/Phương ngữ VN.</li>
                    <li><strong>CA:</strong> Có thể hiểu xuyên văn hóa.</li>
                  </ul>
                  <p className="mt-3 font-semibold text-blue-900 border-t border-blue-200/80 pt-2 text-[13px]">
                    💡 Ưu tiên gán NAT nếu KHÔNG chắc chắn là bản dịch.
                  </p>
                </div>

                <h2 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Chọn Nhãn</h2>
                
                <div className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto pr-2 pb-4">
                  {labels.map((label) => {
                    const isSelected = currentItem.final_label === label.id;
                    return (
                      <button
                        key={label.id}
                        onClick={() => handleAssignLabel(label.id)}
                        className={`
                          w-full text-left px-4 py-3 rounded-lg border-2 transition-all flex justify-between items-center group
                          ${label.base}
                          ${isSelected 
                            ? `${label.border} ring-2 ${label.ring} shadow-sm` 
                            : `border-transparent hover:border-slate-300 opacity-70 hover:opacity-100`
                          }
                        `}
                      >
                        <span className="font-medium">{label.name}</span>
                        {isSelected && <CheckCircle2 size={18} />}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
