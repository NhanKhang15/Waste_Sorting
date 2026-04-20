import { useEffect, useRef, useState } from "react";

interface Props {
  onScan: (file: File, query: string) => void;
  loading: boolean;
}

const ClassificationForm = ({ onScan, loading }: Props) => {
  const [query, setQuery] = useState("find me recyclable waste");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0] ?? null;
    setFile(picked);
  };

  const handleClear = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || loading) return;
    onScan(file, query);
  };

  const canSubmit = !!file && !loading;

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-8 rounded-4xl shadow-sm border border-outline/5 space-y-6"
    >
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

      <div>
        <label className="block text-sm font-bold mb-2">Image</label>
        <div className="flex items-center gap-4 p-4 bg-surface-container-low rounded-2xl">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-primary file:text-white"
          />
          {file ? (
            <button
              type="button"
              onClick={handleClear}
              className="ml-auto text-xs font-bold text-on-surface-variant hover:text-primary transition-colors"
            >
              Clear
            </button>
          ) : null}
        </div>
      </div>

      {previewUrl ? (
        <div>
          <label className="block text-sm font-bold mb-2">Preview</label>
          <div className="bg-surface-container-low rounded-2xl p-4 flex flex-col md:flex-row gap-4 items-start">
            <div className="w-full md:w-64 aspect-video bg-black rounded-xl overflow-hidden shrink-0">
              <img
                src={previewUrl}
                alt="Selected preview"
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex-1 text-xs space-y-1">
              <p className="font-bold text-sm truncate">{file?.name}</p>
              <p className="opacity-60">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : ""}
                {file?.type ? ` • ${file.type}` : ""}
              </p>
              <p className="italic opacity-50 pt-2">
                Kiểm tra lại ảnh rồi nhấn <b>Start Analysis</b> để phân tích.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <button
        type="submit"
        disabled={!canSubmit}
        className={`w-full py-4 rounded-2xl font-bold transition-all ${
          canSubmit
            ? "bg-primary text-white hover:opacity-90"
            : "bg-primary/40 text-white cursor-not-allowed"
        }`}
      >
        {loading ? "Scanning..." : file ? "Start Analysis" : "Chọn ảnh trước"}
      </button>

      <p className="text-[11px] text-on-surface-variant italic">
        Example mapping: <b>bottle</b> becomes recyclable, <b>banana</b> becomes organic...
      </p>
    </form>
  );
};

export default ClassificationForm;
