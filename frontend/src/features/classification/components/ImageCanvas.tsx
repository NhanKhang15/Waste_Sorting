import type { DetectionObject } from "../../../types/waste";

interface Props {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  boxes: DetectionObject[];
}

const ImageCanvas = ({ imageUrl, imageWidth, imageHeight, boxes }: Props) => {
  const safeWidth = imageWidth > 0 ? imageWidth : 1;
  const safeHeight = imageHeight > 0 ? imageHeight : 1;

  return (
    <div className="relative rounded-[2rem] overflow-hidden bg-black aspect-video group shadow-2xl">
      <img src={imageUrl} className="w-full h-full object-contain" alt="Waste Analysis" />

      <div className="absolute inset-0 z-10">
        {boxes.map((box, index) => {
          const left = (box.bbox.x1 / safeWidth) * 100;
          const top = (box.bbox.y1 / safeHeight) * 100;
          const width = (box.bbox.width / safeWidth) * 100;
          const height = (box.bbox.height / safeHeight) * 100;

          return (
            <div
              key={`${box.class_id}-${index}`}
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
