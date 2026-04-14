import type { DetectedObject } from "../hooks/useClassify";

interface Props {
  objects: DetectedObject[];
  status: 'Waiting' | 'Scanning' | 'Success';
}

const MatchResult = ({ objects, status }: Props) => {
  return (
    <div className="space-y-6">
      {/* Status Badges */}
      <div className="flex justify-end gap-2">
        <span className="px-4 py-2 bg-surface-container-highest rounded-full text-xs font-bold">
          {objects.length} objects
        </span>
        <span className={`px-4 py-2 rounded-full text-xs font-bold ${status === 'Waiting' ? 'bg-surface-dim' : 'bg-primary-container text-on-primary-container'}`}>
          {status}
        </span>
      </div>

      {/* Cropped Matches Area */}
      <div className="bg-white p-8 rounded-[2rem] border border-outline/10 min-h-[300px]">
        <h4 className="font-bold mb-6">Cropped matches</h4>
        
        {objects.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {objects.map((obj, i) => (
              <div key={i} className="aspect-square bg-surface-container rounded-xl overflow-hidden border border-outline/5">
                <img src={obj.cropUrl} alt="Match" className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-outline/20 rounded-3xl">
            <p className="text-on-surface-variant text-sm">No cropped match yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchResult;