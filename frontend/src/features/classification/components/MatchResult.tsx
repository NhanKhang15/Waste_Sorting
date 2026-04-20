import { useEffect, useState } from "react";
import type { DetectionObject } from "../../../types/waste";

interface Props {
  imageUrl: string | null;
  objects: DetectionObject[];
  status: "Waiting" | "Scanning" | "Success";
}

interface CropItem {
  detection: DetectionObject;
  dataUrl: string;
}

async function cropDetections(
  imageUrl: string,
  detections: DetectionObject[],
): Promise<CropItem[]> {
  const image = new Image();
  image.crossOrigin = "anonymous";
  image.src = imageUrl;

  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve();
    image.onerror = () => reject(new Error("Unable to load image for cropping."));
  });

  return detections
    .map((detection) => {
      const width = Math.max(1, Math.round(detection.bbox.width));
      const height = Math.max(1, Math.round(detection.bbox.height));
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;

      ctx.drawImage(
        image,
        detection.bbox.x1,
        detection.bbox.y1,
        width,
        height,
        0,
        0,
        width,
        height,
      );

      return { detection, dataUrl: canvas.toDataURL("image/jpeg", 0.85) };
    })
    .filter((item): item is CropItem => item !== null);
}

const MatchResult = ({ imageUrl, objects, status }: Props) => {
  const [crops, setCrops] = useState<CropItem[]>([]);

  useEffect(() => {
    let cancelled = false;

    if (!imageUrl || objects.length === 0) {
      setCrops([]);
      return;
    }

    cropDetections(imageUrl, objects)
      .then((result) => {
        if (!cancelled) setCrops(result);
      })
      .catch(() => {
        if (!cancelled) setCrops([]);
      });

    return () => {
      cancelled = true;
    };
  }, [imageUrl, objects]);

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

      <div className="bg-white p-8 rounded-[2rem] border border-outline/10 min-h-[300px]">
        <h4 className="font-bold mb-6">Cropped matches</h4>

        {crops.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {crops.map((crop, i) => (
              <div
                key={`${crop.detection.class_id}-${i}`}
                className="aspect-square bg-surface-container rounded-xl overflow-hidden border border-outline/5 relative"
              >
                <img
                  src={crop.dataUrl}
                  alt={crop.detection.label}
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-1 left-1 right-1 bg-black/60 text-white text-[10px] font-bold px-2 py-1 rounded flex justify-between">
                  <span>{crop.detection.label}</span>
                  <span>{(crop.detection.confidence * 100).toFixed(0)}%</span>
                </div>
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
