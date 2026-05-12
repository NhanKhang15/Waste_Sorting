import type { DetectedObject } from "../hooks/useClassify";

interface Props {
  objects: DetectedObject[];
  status: "Waiting" | "Scanning" | "Success";
  error?: string | null;
  queryAction?: string;
  wasteGroup?: string;
}

const ObjectCard = ({ obj }: { obj: DetectedObject }) => (
  <div className="bg-surface-container rounded-xl border border-outline/5 p-3 flex flex-col justify-between gap-2">
    <div>
      <p className="text-[9px] uppercase tracking-widest opacity-40">Object</p>
      <p className="mt-1 text-sm font-black leading-tight">{obj.label}</p>
    </div>
    <div className="space-y-1 text-xs">
      <div className="inline-flex rounded-full bg-primary/10 px-2 py-0.5 font-bold text-primary text-[11px]">
        {(obj.confidence * 100).toFixed(1)}%
      </div>
      <p className="text-on-surface-variant text-[10px]">
        {Math.round(obj.rawBbox.width)} × {Math.round(obj.rawBbox.height)} px
      </p>
    </div>
  </div>
);

const MatchResult = ({ objects, status, error, queryAction, wasteGroup }: Props) => {
  const isCount = queryAction === "count";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase opacity-40 tracking-widest">
          {isCount ? "Count Result" : "Matched Objects"}
        </span>
        <div className="flex gap-2">
          <span className="px-3 py-1.5 bg-surface-container-lowest border border-outline/10 rounded-full text-xs font-bold">
            {objects.length} match{objects.length !== 1 ? "es" : ""}
          </span>
          <span
            className={`px-3 py-1.5 rounded-full text-xs font-bold ${
              status === "Waiting"
                ? "bg-surface-container text-on-surface-variant"
                : status === "Scanning"
                  ? "bg-amber-100 text-amber-800"
                  : "bg-primary/10 text-primary"
            }`}
          >
            {status}
          </span>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {isCount && objects.length > 0 && (
        <div className="rounded-2xl bg-primary/5 border border-primary/20 px-6 py-5 flex items-center gap-5">
          <span className="text-5xl font-black text-primary leading-none">{objects.length}</span>
          <div>
            <p className="text-xs text-on-surface-variant">items counted</p>
            {wasteGroup && (
              <p className="text-sm font-bold text-on-surface capitalize">{wasteGroup}</p>
            )}
          </div>
        </div>
      )}

      {objects.length > 0 ? (
        <div className="grid grid-cols-2 gap-3">
          {objects.map((obj, index) => (
            <ObjectCard key={`${obj.label}-${index}`} obj={obj} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-[200px] border-2 border-dashed border-outline/15 rounded-3xl">
          <p className="text-on-surface-variant text-sm italic opacity-50">
            {status === "Waiting" ? "No scan yet" : "No matches for this query"}
          </p>
        </div>
      )}
    </div>
  );
};

export default MatchResult;
