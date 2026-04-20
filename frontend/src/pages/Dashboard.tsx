import { useClassify } from '../features/classification/hooks/useClassify';
import ClassificationForm from '../features/classification/components/ClassificationForm';
import MatchResult from '../features/classification/components/MatchResult';
import ImageCanvas from '../features/classification/components/ImageCanvas';

const Dashboard = () => {
  const { classify, data, loading, error } = useClassify();
  const status: 'Waiting' | 'Scanning' | 'Success' = loading
    ? 'Scanning'
    : data
      ? 'Success'
      : 'Waiting';

  return (
    <div className="min-h-screen bg-[#f5fbef] p-6 lg:p-10 font-sans text-on-surface">
      <main className="max-w-[1400px] mx-auto space-y-8">

        <section className="w-full">
          <header className="mb-6">
            <h1 className="text-5xl font-black italic text-primary tracking-tighter">
              Waste <span className="text-on-surface">Finder.</span>
            </h1>
          </header>
          <ClassificationForm onScan={classify} loading={loading} />
          {error ? (
            <div className="mt-4 px-4 py-3 rounded-2xl bg-red-100 text-red-700 text-sm">
              {error}
            </div>
          ) : null}
        </section>

        {data ? (
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total detections" value={data.response.summary.total_detections} />
            <StatCard label="Unique labels" value={data.response.summary.unique_labels.length} />
            <StatCard
              label="Inference"
              value={`${data.response.summary.inference_ms.toFixed(1)} ms`}
            />
            <StatCard label="Device" value={data.response.model.device} />
          </section>
        ) : null}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
          <div className="flex flex-col">
            <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">Raw Analysis</h3>
            <div className="bg-white p-5 rounded-3xl shadow-sm border border-outline/5 flex-1 min-h-140">
              {data ? (
                <ImageCanvas
                  imageUrl={data.imageUrl}
                  imageWidth={data.response.image.width}
                  imageHeight={data.response.image.height}
                  boxes={data.response.detections}
                />
              ) : (
                <div className="h-full flex items-center justify-center italic text-xs opacity-30 border-2 border-dashed border-primary/10 rounded-2xl">
                  Chờ dữ liệu hình ảnh...
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col">
            <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">Query Matches</h3>
            <div className="bg-white p-5 rounded-3xl shadow-sm border border-outline/5 flex-1 min-h-140">
              <MatchResult
                imageUrl={data?.imageUrl ?? null}
                objects={data?.filteredDetections ?? []}
                status={status}
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          <div className="bg-[#1e1e1e] rounded-3xl overflow-hidden shadow-2xl border border-white/5">
            <div className="p-4 border-b border-white/10 flex justify-between items-center">
              <span className="text-[10px] font-bold text-white/40 uppercase">Generated DSL</span>
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
            </div>
            <div className="p-6 text-white/50 text-xs italic">
              DSL generation coming soon — backend chưa hỗ trợ endpoint này.
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-sm border border-outline/5 overflow-hidden">
            <h3 className="text-[10px] font-bold uppercase opacity-40 mb-4 tracking-widest">
              Abstract Syntax Tree
            </h3>
            <div className="h-55 w-full bg-surface-container-lowest rounded-xl relative flex items-center justify-center">
              <p className="text-[11px] italic opacity-40 px-6 text-center">
                Parse tree sẽ hiển thị ở đây khi backend cung cấp DSL parser.
              </p>
            </div>
          </div>

          {data ? (
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-outline/5">
              <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">
                Class Counts
              </h3>
              <ul className="space-y-2 text-sm">
                {Object.entries(data.response.summary.class_counts).map(([label, count]) => (
                  <li key={label} className="flex justify-between">
                    <span className="font-medium">{label}</span>
                    <span className="opacity-60">{count}</span>
                  </li>
                ))}
                {Object.keys(data.response.summary.class_counts).length === 0 ? (
                  <li className="italic opacity-40">Không phát hiện đối tượng nào.</li>
                ) : null}
              </ul>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-outline/5 opacity-60">
              <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">
                Class Counts
              </h3>
              <p className="italic text-xs opacity-40">Chưa có dữ liệu phân loại.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string | number;
}

const StatCard = ({ label, value }: StatCardProps) => (
  <div className="bg-white p-4 rounded-2xl border border-outline/5 shadow-sm">
    <p className="text-[10px] font-bold uppercase opacity-40 tracking-widest">{label}</p>
    <p className="text-2xl font-black mt-1">{value}</p>
  </div>
);

export default Dashboard;
