import type { DetectedObject } from "../hooks/useClassify";

interface Props {
  imageUrl: string;
  boxes: DetectedObject[];
}

const ImageCanvas = ({ imageUrl, boxes }: Props) => {
  return (
    <div className="relative rounded-[2rem] overflow-hidden bg-black aspect-video group shadow-2xl">
      <img src={imageUrl} className="w-full h-full object-contain" alt="Waste Analysis" />

      <div className="absolute inset-0 z-10">
        {boxes.map((box, index) => {
          const [left, top, width, height] = box.bbox;

          return (
            <div
              key={`${box.classId}-${index}`}
              className="absolute border-2 border-primary-container rounded-lg transition-all hover:scale-105"
              style={{
                left: `${left}%`,
                top: `${top}%`,
                width: `${width}%`,
                height: `${height}%`,
              }}
            >
              <div className="absolute -top-7 left-0 bg-primary-container/90 backdrop-blur-md text-white text-[10px] font-bold px-2 py-1 rounded shadow-lg flex items-center gap-1">
                <span className="material-symbols-outlined text-[12px]">target</span>
                {box.label.toUpperCase()} {(box.confidence * 100).toFixed(1)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ImageCanvas;
