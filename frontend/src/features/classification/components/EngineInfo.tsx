import type { WasteEngineResultResponse } from "../../../types/waste";

interface Props {
  engineUsed: string;
  decisionReason: string;
  primaryResult: WasteEngineResultResponse | null;
  fallbackResult: WasteEngineResultResponse | null;
}

const ENGINE_LABELS: Record<string, string> = {
  custom_waste_detector: "Custom Waste Model",
  coco_rule_map: "COCO + Rule Map",
  merged: "Hybrid Merge",
};

const EngineStatCard = ({
  label,
  result,
  isActive,
}: {
  label: string;
  result: WasteEngineResultResponse;
  isActive: boolean;
}) => (
  <div
    className={`rounded-2xl px-4 py-3 border ${
      isActive
        ? "border-primary/30 bg-primary/5"
        : "border-outline/10 bg-surface-container-lowest"
    }`}
  >
    <div className="flex items-center justify-between mb-2">
      <p className="text-[9px] font-bold uppercase tracking-widest opacity-50">{label}</p>
      {isActive && (
        <span className="text-[9px] font-bold text-primary bg-primary/10 rounded-full px-2 py-0.5">
          USED
        </span>
      )}
    </div>
    <div className="flex gap-6 text-sm">
      <div>
        <p className="text-[10px] opacity-40 mb-0.5">Matches</p>
        <p className="font-black text-base">{result.match_count}</p>
      </div>
      <div>
        <p className="text-[10px] opacity-40 mb-0.5">Max Conf</p>
        <p className="font-black text-base">
          {result.max_match_confidence !== null && result.max_match_confidence !== undefined
            ? `${(result.max_match_confidence * 100).toFixed(1)}%`
            : "—"}
        </p>
      </div>
      <div>
        <p className="text-[10px] opacity-40 mb-0.5">Detections</p>
        <p className="font-black text-base">{result.detections.length}</p>
      </div>
    </div>
  </div>
);

const EngineInfo = ({ engineUsed, decisionReason, primaryResult, fallbackResult }: Props) => {
  const isPrimary = engineUsed === "custom_waste_detector";
  const isMerged = engineUsed === "merged";
  const engineLabel = ENGINE_LABELS[engineUsed] ?? engineUsed;

  return (
    <div className="space-y-3">
      <div
        className={`rounded-2xl px-4 py-3 flex items-center gap-3 ${
          isMerged
            ? "bg-sky-50 border border-sky-200"
            : isPrimary
            ? "bg-green-50 border border-green-200"
            : "bg-amber-50 border border-amber-200"
        }`}
      >
        <div
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            isMerged
              ? "bg-sky-500"
              : isPrimary
              ? "bg-green-500"
              : "bg-amber-500"
          }`}
        />
        <div>
          <p className="text-[9px] font-bold uppercase tracking-widest opacity-50">Engine used</p>
          <p
            className={`text-sm font-bold ${
              isMerged
                ? "text-sky-800"
                : isPrimary
                ? "text-green-800"
                : "text-amber-800"
            }`}
          >
            {engineLabel}
          </p>
        </div>
      </div>

      <div className="rounded-2xl bg-surface-container-low px-4 py-3 border border-outline/10">
        <p className="text-[9px] font-bold uppercase tracking-widest opacity-50 mb-1">Decision</p>
        <p className="text-xs text-on-surface-variant leading-relaxed">{decisionReason}</p>
      </div>

      {primaryResult && (
        <EngineStatCard
          label="Primary (Custom Model)"
          result={primaryResult}
          isActive={isPrimary || isMerged}
        />
      )}
      {fallbackResult && (
        <EngineStatCard
          label="Fallback (COCO)"
          result={fallbackResult}
          isActive={!isPrimary}
        />
      )}
    </div>
  );
};

export default EngineInfo;
