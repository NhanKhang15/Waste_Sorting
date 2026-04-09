import React from 'react';
import { useClassify } from '../features/classification/hooks/useClassify';
import ImageCanvas from '../features/classification/components/ImageCanvas';
import DSLEditor from '../features/classification/components/DSLEditor';
import TreeVisualizer from '../features/classification/components/TreeVisualizer';

const Dashboard = () => {
  const { classify, data, loading } = useClassify();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) classify(file);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row">
      {/* 1. Sidebar (Bạn có thể tách thành component riêng sau) */}
      <aside className="w-64 bg-surface-container-low p-8 border-r border-outline/10">
        <h2 className="text-primary text-2xl font-black mb-10">WasteWise</h2>
        <input type="file" onChange={handleFileUpload} className="hidden" id="upload" />
        <label htmlFor="upload" className="block w-full py-4 bg-primary text-white text-center rounded-full cursor-pointer hover:opacity-90 transition-all font-bold">
          {loading ? 'Analyzing...' : 'New Scan'}
        </label>
      </aside>

      {/* 2. Main Content Canvas */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="mb-10">
          <h1 className="text-6xl font-headline font-extrabold italic text-on-surface">Scan <span className="text-primary">Waste.</span></h1>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cột trái & giữa: YOLO Viewport & Parse Tree */}
          <div className="lg:col-span-2 space-y-8">
            {data ? (
              <>
                <ImageCanvas imageUrl={data.imageUrl} boxes={data.detectedObjects} />
                <div className="bg-white p-6 rounded-[2rem] shadow-sm">
                   <h3 className="text-xl font-bold mb-4">Abstract Syntax Tree (PPL Core)</h3>
                   <TreeVisualizer data={data.parseTree} />
                </div>
              </>
            ) : (
              <div className="aspect-video bg-surface-container-low rounded-[2rem] flex items-center justify-center border-4 border-dashed border-outline/20 italic text-on-surface-variant">
                Vui lòng upload ảnh để bắt đầu phân tích...
              </div>
            )}
          </div>

          {/* Cột phải: Generated DSL & Result */}
          <aside className="space-y-6">
            <div className="h-[400px]">
               <DSLEditor code={data?.dslCode || "// DSL will be generated here..."} />
            </div>
            
            {data && (
              <div className="bg-primary text-white p-6 rounded-3xl shadow-lg">
                <h4 className="text-xs uppercase font-bold tracking-widest opacity-80 mb-2">Final Verdict</h4>
                <p className="text-lg font-bold">{data.result}</p>
              </div>
            )}
          </aside>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;