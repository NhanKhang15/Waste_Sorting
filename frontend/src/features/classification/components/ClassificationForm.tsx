import { useState } from "react";
import type { FormEvent } from "react";

interface Props {
  onScan: (file: File, query: string) => Promise<void> | void;
  loading: boolean;
}

const ClassificationForm = ({ onScan, loading }: Props) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [query, setQuery] = useState("find me recyclable waste");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedFile || loading || !query.trim()) {
      return;
    }

    await onScan(selectedFile, query.trim());
  };

  return (
    <form
      className="bg-white p-8 rounded-[2rem] shadow-sm border border-outline/5 space-y-6"
      onSubmit={handleSubmit}
    >
      <div>
        <label className="block text-sm font-bold mb-2">Image</label>
        <div className="flex items-center gap-4 p-4 bg-surface-container-low rounded-2xl">
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-primary file:text-white"
          />
        </div>
        <p className="mt-2 text-xs text-on-surface-variant">
          {selectedFile
            ? `Selected: ${selectedFile.name}`
            : "Choose an image, then run YOLOv26 analysis."}
        </p>
      </div>

      <div>
        <label className="block text-sm font-bold mb-2">DSL Query</label>
        <textarea
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          rows={3}
          className="w-full p-4 rounded-2xl bg-surface-container-low text-sm outline-none border border-outline/10 focus:border-primary"
          placeholder='find recyclable waste where confidence >= 0.8 and label = bottle'
        />
        <p className="mt-2 text-xs text-on-surface-variant">
          Examples: <code>find me recyclable waste</code>,{" "}
          <code>count organic waste where confidence &gt;= 0.6</code>,{" "}
          <code>find recyclable waste where label = bottle</code>.
        </p>
      </div>

      <button
        type="submit"
        disabled={!selectedFile || loading || !query.trim()}
        className={`w-full py-4 rounded-2xl font-bold transition-all ${
          loading || !selectedFile || !query.trim()
            ? "bg-primary/50 text-white/80 cursor-not-allowed"
            : "bg-primary text-white"
        }`}
      >
        {loading ? "Scanning..." : "Start Analysis"}
      </button>

      <p className="text-[11px] text-on-surface-variant italic">
        Frontend now sends the DSL query to the waste backend and can render the parse tree returned by ANTLR.
      </p>
    </form>
  );
};

export default ClassificationForm;
