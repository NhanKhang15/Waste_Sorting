import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../../../api/client";
import { detectWaste } from "../services/api";
import type { DetectionObject, DetectionResponse } from "../../../types/waste";

export interface UseClassifyData {
  imageUrl: string;
  response: DetectionResponse;
  filteredDetections: DetectionObject[];
  query: string;
}

function filterDetections(
  detections: DetectionObject[],
  query: string,
): DetectionObject[] {
  const trimmed = query.trim().toLowerCase();
  if (!trimmed) return detections;

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  const matched = detections.filter((det) =>
    tokens.some((token) => det.label.toLowerCase().includes(token)),
  );

  return matched.length > 0 ? matched : detections;
}

export const useClassify = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<UseClassifyData | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, []);

  const classify = useCallback(async (file: File, query: string) => {
    setLoading(true);
    setError(null);

    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
    }
    const imageUrl = URL.createObjectURL(file);
    objectUrlRef.current = imageUrl;

    try {
      const response = await detectWaste(file);
      setData({
        imageUrl,
        response,
        filteredDetections: filterDetections(response.detections, query),
        query,
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unknown error while calling the detection service.";
      setError(message);
      setData(null);
      URL.revokeObjectURL(imageUrl);
      objectUrlRef.current = null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { classify, data, loading, error };
};
