import { useState } from "react";

interface Props {
  onScan: (file: File, query: string) => void;
  loading: boolean;
}

const ClassificationForm = ({ onScan, loading }: Props) => {
  const [query, setQuery] = useState("find me recyclable waste");

  return (
    <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-outline/5 space-y-6">
      {/* Input Query */}
      <div>
        <label className="block text-sm font-bold mb-2">Query</label>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full p-4 bg-surface-container-low rounded-2xl border-none focus:ring-2 focus:ring-primary"
          placeholder="e.g., find me recyclable waste"
        />
      </div>

      {/* Upload Image */}
      <div>
        <label className="block text-sm font-bold mb-2">Image</label>
        <div className="flex items-center gap-4 p-4 bg-surface-container-low rounded-2xl">
          <input type="file" onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onScan(file, query);
          }} className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-primary file:text-white" />
        </div>
      </div>

      <button className={`w-full py-4 rounded-2xl font-bold transition-all ${loading ? 'bg-primary/50' : 'bg-primary text-white'}`}>
        {loading ? 'Scanning...' : 'Start Analysis'}
      </button>

      <p className="text-[11px] text-on-surface-variant italic">
        Example mapping: <b>bottle</b> becomes recyclable, <b>banana</b> becomes organic...
      </p>
    </div>
  );
};

export default ClassificationForm;