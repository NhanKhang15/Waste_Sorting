import { useClassify } from '../features/classification/hooks/useClassify';
import DSLEditor from '../features/classification/components/DSLEditor';
import TreeVisualizer from '../features/classification/components/TreeVisualizer';
import ClassificationForm from '../features/classification/components/ClassificationForm';
import MatchResult from '../features/classification/components/MatchResult';
import ImageCanvas from '../features/classification/components/ImageCanvas';

const Dashboard = () => {
  const { classify, data, loading } = useClassify();

  return (
    <div className="min-h-screen bg-[#f5fbef] p-6 lg:p-10 font-sans text-on-surface">
      <main className="max-w-[1400px] mx-auto space-y-8">
        
        {/* SECTION 1: Điều khiển - Trải dài toàn bộ chiều rộng */}
        <section className="w-full">
          <header className="mb-6">
            <h1 className="text-5xl font-black italic text-primary tracking-tighter">
              Waste <span className="text-on-surface">Finder.</span>
            </h1>
          </header>
          <ClassificationForm onScan={classify} loading={loading} />
        </section>

        {/* SECTION 2: Lưới nội dung chính (12 cột) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* CỘT TRÁI (8 Cột): Hiển thị hình ảnh */}
          <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Khối Ảnh Gốc */}
            <div className="flex flex-col">
              <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">Raw Analysis</h3>
              <div className="bg-white p-4 rounded-3xl shadow-sm border border-outline/5 flex-1 min-h-[350px]">
                {data ? (
                  <ImageCanvas imageUrl={data.imageUrl} boxes={data.detectedObjects} />
                ) : (
                  <div className="h-full flex items-center justify-center italic text-xs opacity-30 border-2 border-dashed border-primary/10 rounded-2xl">
                    Chờ dữ liệu hình ảnh...
                  </div>
                )}
              </div>
            </div>

            {/* Khối Ảnh Cắt */}
            <div className="flex flex-col">
              <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">Query Matches</h3>
              <div className="bg-white p-4 rounded-3xl shadow-sm border border-outline/5 flex-1 min-h-[350px]">
                <MatchResult 
                  objects={data?.detectedObjects || []} 
                  status={loading ? 'Scanning' : (data ? 'Success' : 'Waiting')} 
                />
              </div>
            </div>
          </div>

          {/* CỘT PHẢI (4 Cột): Logic PPL */}
          <aside className="lg:col-span-4 space-y-6">
            <div className="bg-[#1e1e1e] rounded-3xl overflow-hidden shadow-2xl border border-white/5">
              <div className="p-4 border-b border-white/10 flex justify-between items-center">
                <span className="text-[10px] font-bold text-white/40 uppercase">Generated DSL</span>
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              </div>
              {/* Giới hạn chiều cao DSL để không bị quá dài */}
              <div className="max-h-[250px] overflow-auto">
                <DSLEditor code={data?.dslCode || "// Waiting for input..."} />
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl shadow-sm border border-outline/5 overflow-hidden"> 
              <h3 className="text-[10px] font-bold uppercase opacity-40 mb-4 tracking-widest">
                Abstract Syntax Tree
              </h3>
              
              {/* Đảm bảo container này có chiều cao cố định và relative */}
              <div className="h-[300px] w-full bg-surface-container-lowest rounded-xl relative">
                {data?.parseTree ? (
                  <TreeVisualizer data={data.parseTree} />
                ) : (
                  <div className="h-full flex items-center justify-center text-[10px] italic opacity-20">
                    Tree will render here
                  </div>
                )}
              </div>
            </div>
          </aside>

        </div>
      </main>
    </div>
  );
};

export default Dashboard;