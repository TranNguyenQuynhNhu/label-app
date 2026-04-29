import React, { useState, useEffect } from 'react';
import { Download, ChevronRight, ChevronLeft, Trash2, CheckCircle2, Info, BookOpen, User, FastForward, MessageSquare, Search, Zap } from 'lucide-react';

// 1. Import chính xác 3 nguồn dữ liệu
import MMLU_PROX from './data/mmlu_prox.json';
import SEA_EXAM from './data/seaexam.json';
import VMLU from './data/vmlu.json';

// 2. Gộp tất cả dữ liệu và gán benchmark_name[cite: 3, 4]
const ALL_MOCK_DATA = [
  ...MMLU_PROX.map(item => ({ ...item, benchmark_name: "MMLU-PROX" })),
  ...SEA_EXAM.map(item => ({ ...item, benchmark_name: "SEA-EXAM" })),
  ...VMLU.map(item => ({ ...item, benchmark_name: "VMLU" }))
];

const NAT_TRA_LABELS = [
  { id: 'NAT', name: 'NAT', base: 'bg-green-100 text-green-800', border: 'border-green-600' },
  { id: 'TRA', name: 'TRA', base: 'bg-blue-100 text-blue-800', border: 'border-blue-600' },
  { id: 'ADP', name: 'ADP', base: 'bg-cyan-100 text-cyan-800', border: 'border-cyan-600' },
  { id: 'UNK', name: 'UNK', base: 'bg-slate-100 text-slate-800', border: 'border-slate-500' },
];

const CS_CA_LABELS = [
  { id: 'CS-L', name: 'CS-L', base: 'bg-purple-100 text-purple-800', border: 'border-purple-600' },
  { id: 'CS-E', name: 'CS-E', base: 'bg-purple-100 text-purple-800', border: 'border-purple-600' },
  { id: 'CS-P', name: 'CS-P', base: 'bg-purple-100 text-purple-800', border: 'border-purple-600' },
  { id: 'CS-H', name: 'CS-H', base: 'bg-purple-100 text-purple-800', border: 'border-purple-600' },
  { id: 'CA', name: 'CA', base: 'bg-rose-100 text-rose-800', border: 'border-rose-600' },
  { id: 'UNK', name: 'UNK', base: 'bg-slate-100 text-slate-800', border: 'border-slate-500' },
];

export default function App() {
  const [items, setItems] = useState(ALL_MOCK_DATA);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [inputValue, setInputValue] = useState("1"); 
  const [isFinished, setIsFinished] = useState(false);
  const [annotator, setAnnotator] = useState("");

  const currentItem = items[currentIndex];
  const progress = Math.round(((currentIndex + 1) / items.length) * 100);
  
  const labeledCount = items.filter(item => item.nat_tra_adp_label && item.cs_ca_label).length;
  const isCurrentFullyLabeled = Boolean(currentItem?.nat_tra_adp_label && currentItem?.cs_ca_label);

  useEffect(() => {
    setInputValue((currentIndex + 1).toString());
  }, [currentIndex]);

  const handleInputChange = (e) => {
    let val = e.target.value.replace(/[^0-9]/g, '');
    if (val !== "") {
      let num = parseInt(val, 10);
      if (num > items.length) num = items.length;
      if (num >= 1 && num <= items.length) setCurrentIndex(num - 1);
    }
    setInputValue(val);
  };

  const handleInputBlur = () => {
    setInputValue((currentIndex + 1).toString());
  };

  const handleNext = () => {
    if (currentIndex < items.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  // Nhảy đến câu chưa gán nhãn tiếp theo của toàn bộ dataset[cite: 4]
  const handleJumpToNextUnlabeled = () => {
    let nextIndex = items.findIndex((item, idx) => idx > currentIndex && !(item.nat_tra_adp_label && item.cs_ca_label));
    if (nextIndex === -1) {
      nextIndex = items.findIndex((item, idx) => idx < currentIndex && !(item.nat_tra_adp_label && item.cs_ca_label));
    }
    if (nextIndex !== -1 && nextIndex !== currentIndex) {
      setCurrentIndex(nextIndex);
    } else {
      alert("Tất cả các câu đã được gán nhãn đầy đủ!");
    }
  };

  // Nhảy đến câu có nhãn UNK[cite: 4]
  const handleJumpToNextUnk = () => {
    let nextIndex = items.findIndex((item, idx) => 
      idx > currentIndex && (item.nat_tra_adp_label === 'UNK' || item.cs_ca_label === 'UNK')
    );
    if (nextIndex === -1) {
      nextIndex = items.findIndex((item, idx) => 
        idx < currentIndex && (item.nat_tra_adp_label === 'UNK' || item.cs_ca_label === 'UNK')
      );
    }
    if (nextIndex !== -1 && nextIndex !== currentIndex) {
      setCurrentIndex(nextIndex);
    } else {
      alert("Không tìm thấy mẫu nào khác có nhãn UNK.");
    }
  };

  // Hàm mới: Nhảy đến câu chưa gán đầu tiên của một Benchmark cụ thể[cite: 4]
  const handleJumpToBenchmarkUnlabeled = (benchmarkName) => {
    const nextIndex = items.findIndex(item => 
      item.benchmark_name === benchmarkName && !(item.nat_tra_adp_label && item.cs_ca_label)
    );
    
    if (nextIndex !== -1) {
      setCurrentIndex(nextIndex);
    } else {
      alert(`Tất cả các câu trong ${benchmarkName} đã được gán nhãn đầy đủ!`);
    }
  };

  const handleAssignNatTra = (labelId) => {
    const updatedItems = [...items];
    updatedItems[currentIndex].nat_tra_adp_label = updatedItems[currentIndex].nat_tra_adp_label === labelId ? null : labelId;
    setItems(updatedItems);
  };

  const handleAssignCsCa = (labelId) => {
    const updatedItems = [...items];
    updatedItems[currentIndex].cs_ca_label = updatedItems[currentIndex].cs_ca_label === labelId ? null : labelId;
    setItems(updatedItems);
  };

  const handleRationaleChange = (e) => {
    const updatedItems = [...items];
    updatedItems[currentIndex].rationale = e.target.value;
    setItems(updatedItems);
  };

  const handleClearLabel = () => {
    const updatedItems = [...items];
    updatedItems[currentIndex].nat_tra_adp_label = null;
    updatedItems[currentIndex].cs_ca_label = null;
    updatedItems[currentIndex].rationale = "";
    setItems(updatedItems);
  };

  const handleExportJSON = () => {
    if (!annotator.trim()) {
      alert("Vui lòng nhập tên trước khi xuất file!");
      return;
    }
    const annotatedItems = items.filter(item => item.nat_tra_adp_label && item.cs_ca_label);
    if (annotatedItems.length === 0) {
      alert("Chưa có mẫu nào được đánh nhãn đầy đủ để xuất!");
      return;
    }

    const exportData = annotatedItems.map(item => {
      const finalLabel = `${item.nat_tra_adp_label}-${item.cs_ca_label}`;
      let formattedOptions = [];
      if (item.options && Array.isArray(item.options)) {
        formattedOptions = item.options.map(opt => {
          if (typeof opt === 'string') {
            const parts = opt.split('.');
            return { id: parts[0].trim(), text: parts.slice(1).join('.').trim() };
          }
          return opt;
        });
      }

      return {
        benchmark_name: item.benchmark_name, 
        sample_id: item.sample_id || item.id || "",
        question: item.question,
        options: formattedOptions,
        answer: item.answer || "",
        nat_tra_adp_label: item.nat_tra_adp_label,
        cs_ca_label: item.cs_ca_label,
        final_label: finalLabel,
        annotator: annotator.trim(),
        rationale: item.rationale || "",
        timestamp: new Date().toISOString(),
        is_annotated: true,
        metadata: item.metadata || {}
      };
    });

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    const safeName = annotator.trim().replace(/\s+/g, '_');
    downloadAnchorNode.setAttribute("download", `${safeName}_${annotatedItems.length}_labels.json`);
    document.body.appendChild(downloadAnchorNode); 
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm sticky top-0 z-10">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="text-indigo-600" />
            Labeling Studio
          </h1>
          <p className="text-sm text-slate-500 mt-1">Đã đánh nhãn: {labeledCount} / {items.length} mẫu</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center bg-slate-100 rounded-lg px-3 py-2 border border-slate-200 focus-within:border-indigo-500 transition-all">
            <User size={16} className="text-slate-400 mr-2" />
            <input 
              type="text" 
              placeholder="Tên Annotator..." 
              value={annotator}
              onChange={(e) => setAnnotator(e.target.value)}
              className="bg-transparent border-none outline-none text-sm w-40"
            />
          </div>
          <button onClick={handleExportJSON} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium shadow-sm">
            <Download size={18} /> Xuất JSON
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col md:flex-row gap-8">
        {isFinished ? (
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 p-12 flex flex-col items-center justify-center text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle2 size={40} className="text-green-600" />
            </div>
            <h2 className="text-3xl font-bold text-slate-800 mb-3">Hoàn tất!</h2>
            <button onClick={() => setIsFinished(false)} className="px-6 py-3 rounded-lg border border-slate-300 font-medium hover:bg-slate-50">Quay lại kiểm tra</button>
          </div>
        ) : (
          <>
            <div className="flex-1 flex flex-col gap-4">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-1 flex-1 flex flex-col overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50">
                  <span className="text-sm font-medium text-slate-600 flex items-center gap-2">
                    <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight">{currentItem.benchmark_name}</span>
                    <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded text-xs font-mono">{currentItem.sample_id || currentItem.id}</span>
                    Mẫu #{currentIndex + 1}
                  </span>
                  {isCurrentFullyLabeled && (
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-200 text-slate-700 flex items-center gap-1">
                      Đã gán: {currentItem.nat_tra_adp_label}-{currentItem.cs_ca_label}
                      <button onClick={handleClearLabel} className="hover:text-red-500 ml-1"><Trash2 size={12}/></button>
                    </span>
                  )}
                </div>

                <div className="flex-1 p-8 bg-slate-50/50 overflow-y-auto">
                  <div className="max-w-3xl mx-auto">
                    <div className="mb-6">
                      <span className="text-xs font-bold text-indigo-500 uppercase tracking-wider mb-2 block">Câu hỏi</span>
                      <h3 className="text-xl font-semibold text-slate-800 leading-relaxed bg-white p-5 rounded-lg border border-slate-200 shadow-sm">{currentItem.question}</h3>
                    </div>
                    <div className="space-y-3">
                      {currentItem.options && Array.isArray(currentItem.options) && currentItem.options.map((opt, idx) => {
                        const isString = typeof opt === 'string';
                        const optId = isString ? opt.split('.')[0].trim() : opt.id;
                        const optText = isString ? opt.split('.').slice(1).join('.').trim() : opt.text;
                        const isCorrect = currentItem.answer && currentItem.answer === optId;
                        return (
                          <div key={idx} className={`p-4 rounded-lg border-2 flex items-start gap-4 ${isCorrect ? 'border-green-400 bg-green-50 shadow-sm' : 'border-slate-200 bg-white'}`}>
                            <span className={`font-bold flex-shrink-0 mt-0.5 ${isCorrect ? 'text-green-600' : 'text-slate-400'}`}>{optId}.</span>
                            <span className="text-slate-700 leading-relaxed">{optText}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
                <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2 mb-2">
                  <MessageSquare size={14} /> Rationale (Lý giải lựa chọn)
                </label>
                <textarea 
                  value={currentItem.rationale || ""}
                  onChange={handleRationaleChange}
                  placeholder="Nhập lý do tại sao bạn chọn các nhãn này..."
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-1 focus:ring-indigo-500 outline-none h-20 resize-none"
                />
              </div>

              <div className="mt-2 flex flex-col">
                <div className="flex justify-between items-center mb-1">
                  <button onClick={handlePrev} disabled={currentIndex === 0} className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-md bg-white border border-slate-300 disabled:opacity-50 transition-colors shadow-sm focus:outline-none"><ChevronLeft size={16} /> Quay lại</button>
                  
                  <div className="flex flex-col items-center gap-2">
                    {/* Hàng 1: Navigation chính[cite: 4] */}
                    <div className="flex items-center gap-1.5 bg-white px-2.5 py-1 rounded-md border border-slate-300 shadow-sm">
                      <input type="text" value={inputValue} onChange={handleInputChange} onBlur={handleInputBlur} className="border border-slate-200 rounded px-1 py-0.5 text-sm font-semibold text-indigo-700 w-12 text-center" />
                      <span className="text-sm text-slate-500 font-medium">/ {items.length}</span>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={handleJumpToNextUnlabeled} className="flex items-center gap-1 text-[11px] font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full hover:bg-indigo-100 transition-colors"><FastForward size={12} /> Đến câu chưa gán</button>
                      <button onClick={handleJumpToNextUnk} className="flex items-center gap-1 text-[11px] font-medium text-slate-600 bg-slate-200 px-2 py-0.5 rounded-full hover:bg-slate-300 transition-colors"><Search size={12} /> Đến câu có nhãn UNK</button>
                    </div>
                    
                    {/* Hàng 2: 3 Nút nhảy nhanh theo Benchmark mới thêm */}
                    <div className="flex gap-2 border-t border-slate-200 pt-2">
                      <button onClick={() => handleJumpToBenchmarkUnlabeled("MMLU-PROX")} className="flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-1 rounded border border-amber-200 hover:bg-amber-100 transition-colors"><Zap size={10} /> MMLU-PROX</button>
                      <button onClick={() => handleJumpToBenchmarkUnlabeled("SEA-EXAM")} className="flex items-center gap-1 text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-200 hover:bg-blue-100 transition-colors"><Zap size={10} /> SEA-EXAM</button>
                      <button onClick={() => handleJumpToBenchmarkUnlabeled("VMLU")} className="flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-200 hover:bg-emerald-100 transition-colors"><Zap size={10} /> VMLU</button>
                    </div>
                  </div>

                  <button 
                    onClick={() => currentIndex === items.length - 1 ? setIsFinished(true) : handleNext()} 
                    disabled={!isCurrentFullyLabeled} 
                    className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-md border transition-colors shadow-sm focus:outline-none ${!isCurrentFullyLabeled ? 'bg-slate-100 text-slate-400 border-slate-200' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'}`}
                  >
                    {currentIndex === items.length - 1 ? 'Hoàn tất' : 'Tiếp theo'} <ChevronRight size={16} />
                  </button>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 mt-3"><div className="bg-indigo-600 h-1.5 rounded-full transition-all" style={{ width: `${progress}%` }}></div></div>
              </div>
            </div>

            <div className="w-full md:w-80 flex flex-col gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 sticky top-24">
                <div className="bg-amber-50 p-4 rounded-lg border border-amber-200 mb-5 text-sm text-amber-800 shadow-sm leading-relaxed">
                  <h3 className="font-bold mb-2 flex items-center gap-1.5 text-amber-900"><Info size={16}/> Lưu ý quan trọng</h3>
                  <p className="font-medium text-[13px]">
                    Vui lòng đọc kỹ <strong className="text-amber-900">Guideline và định nghĩa các nhãn</strong> trước khi tiến hành đánh nhãn.<br/><br/>
                    Bạn <strong className="underline">bắt buộc</strong> phải chọn 1 nhãn ở nhóm <strong className="text-amber-900">Text Origin</strong> và 1 nhãn ở nhóm <strong className="text-amber-900">Cultural Sensitivity</strong> để có thể sang câu tiếp theo.
                  </p>
                </div>

                <div className="max-h-[55vh] overflow-y-auto pr-2 pb-4 space-y-6">
                  <div>
                    <h2 className="text-sm font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 uppercase tracking-wider">
                      1. Text origin (NAT/TRA/ADP)
                    </h2>
                    <div className="flex flex-col gap-2">
                      {NAT_TRA_LABELS.map((label) => (
                        <button key={label.id} onClick={() => handleAssignNatTra(label.id)} className={`w-full text-left px-4 py-2.5 rounded-lg border-2 transition-all flex justify-between items-center text-sm ${label.base} ${currentItem?.nat_tra_adp_label === label.id ? `${label.border} border-[3px] font-bold shadow-md` : 'border-transparent opacity-70 font-medium hover:border-slate-200'}`}>
                          <span>{label.id}</span>
                          {currentItem?.nat_tra_adp_label === label.id && <CheckCircle2 size={16} />}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h2 className="text-sm font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 uppercase tracking-wider">
                      2. Cultural sensitivity (CS/CA)
                    </h2>
                    <div className="flex flex-col gap-2">
                      {CS_CA_LABELS.map((label) => (
                        <button key={label.id} onClick={() => handleAssignCsCa(label.id)} className={`w-full text-left px-4 py-2.5 rounded-lg border-2 transition-all flex justify-between items-center text-sm ${label.base} ${currentItem?.cs_ca_label === label.id ? `${label.border} border-[3px] font-bold shadow-md` : 'border-transparent opacity-70 font-medium hover:border-slate-200'}`}>
                          <span>{label.id}</span>
                          {currentItem?.cs_ca_label === label.id && <CheckCircle2 size={16} />}
                        </button>
                      ))}
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