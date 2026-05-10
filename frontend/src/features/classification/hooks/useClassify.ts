import { useEffect, useRef, useState } from "react";

import { ApiError } from "../../../api/client";
import type {
  DetectionObjectResponse,
  WasteFindResponse,
  WasteQueryTreeNodeResponse,
} from "../../../types/waste";
import { findWaste } from "../services/api";

export interface DetectedObject {
  classId: number;
  label: string;
  confidence: number;
  bbox: number[];
  rawBbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  };
}

export interface UseClassifyData {
  imageUrl: string;
  detectedObjects: DetectedObject[];
  dslCode: string;
  parseTree: WasteQueryTreeNodeResponse;
  result: string;
}

const clampPercentage = (value: number) => Math.max(0, Math.min(100, value));

const mapDetectionsToDetectedObjects = (
  detections: DetectionObjectResponse[],
  response: WasteFindResponse,
): DetectedObject[] => {
  const imageWidth = response.image.width;
  const imageHeight = response.image.height;

  return detections.map((detection) => ({
    classId: detection.class_id,
    label: detection.label,
    confidence: detection.confidence,
    bbox: [
      clampPercentage((detection.bbox.x1 / imageWidth) * 100),
      clampPercentage((detection.bbox.y1 / imageHeight) * 100),
      clampPercentage((detection.bbox.width / imageWidth) * 100),
      clampPercentage((detection.bbox.height / imageHeight) * 100),
    ],
    rawBbox: {
      x1: detection.bbox.x1,
      y1: detection.bbox.y1,
      x2: detection.bbox.x2,
      y2: detection.bbox.y2,
      width: detection.bbox.width,
      height: detection.bbox.height,
    },
  }));
};

const buildResultSummary = (response: WasteFindResponse) => {
  const targetGroup = response.waste_group;
  const action = response.query_action;
  const engine = response.engine_used;
  const count = response.match_count;

  if (count === 0) {
    return `DSL query "${response.normalized_query}" produced no ${targetGroup} match using ${engine}.`;
  }

  const labelFilter = response.label_filter
    ? ` with label filter "${response.label_filter}"`
    : "";
  const confidenceFilter =
    response.minimum_confidence !== null &&
    response.minimum_confidence !== undefined &&
    response.confidence_operator
      ? ` and confidence ${response.confidence_operator} ${response.minimum_confidence}`
      : "";

  return `${action} query matched ${count} ${targetGroup} item(s)${labelFilter}${confidenceFilter} using ${engine}.`;
};

const getErrorMessage = (error: unknown) => {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Unexpected error while calling the waste backend.";
};

export const useClassify = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<UseClassifyData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
      }
    };
  }, []);

  const classify = async (file: File, query: string) => {
    setLoading(true);
    setError(null);

    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
    }

    const imageUrl = URL.createObjectURL(file);
    objectUrlRef.current = imageUrl;

    try {
      const response = await findWaste(file, query);

      setData({
        imageUrl,
        detectedObjects: mapDetectionsToDetectedObjects(response.detections, response),
        dslCode: response.normalized_query,
        parseTree: response.parse_tree,
        result: buildResultSummary(response),
      });
    } catch (caughtError) {
      setData(null);
      setError(getErrorMessage(caughtError));
    } finally {
      setLoading(false);
    }
  };

  return { classify, data, loading, error };
};
