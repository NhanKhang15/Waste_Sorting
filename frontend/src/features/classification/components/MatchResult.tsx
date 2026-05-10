import type { DetectedObject } from "../hooks/useClassify";

interface Props {
  objects: DetectedObject[];
  status: "Waiting" | "Scanning" | "Success";
  error?: string | null;
}

const MatchResult = ({ objects, status, error }: Props) => {
  return (
    <div className="space-y-6">
      <div className="flex justify-end gap-2">
        <span className="px-4 py-2 bg-surface-container-highest rounded-full text-xs font-bold">
          {objects.length} objects
        </span>
        <span
          className={`px-4 py-2 rounded-full text-xs font-bold ${
            status === "Waiting"
              ? "bg-surface-dim"
              : "bg-primary-container text-on-primary-container"
          }`}
        >
          {status}
        </span>
      </div>

      {error ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="bg-white p-8 rounded-[2rem] border border-outline/10 min-h-[300px]">
        <h4 className="font-bold mb-6">Detected objects</h4>

        {objects.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {objects.map((obj, index) => (
              <div
                key={`${obj.label}-${index}`}
                className="aspect-square bg-surface-container rounded-xl overflow-hidden border border-outline/5 p-4 flex flex-col justify-between"
              >
                <div>
                  <p className="text-[10px] uppercase tracking-widest opacity-40">Object</p>
                  <p className="mt-2 text-base font-black">{obj.label}</p>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="inline-flex rounded-full bg-primary/10 px-3 py-1 font-bold text-primary">
                    {(obj.confidence * 100).toFixed(1)}%
                  </div>
                  <p className="text-on-surface-variant">
                    Box: {Math.round(obj.rawBbox.width)} x {Math.round(obj.rawBbox.height)} px
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-outline/20 rounded-3xl">
            <p className="text-on-surface-variant text-sm">No detections yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchResult;
