import { useEffect, useRef, useState } from "react";

import { ApiError } from "../../../api/client";
import type {
  DetectionObjectResponse,
  TokenInfoResponse,
  WasteEngineResultResponse,
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
  matchedObjects: DetectedObject[];
  dslCode: string;
  parseTree: WasteQueryTreeNodeResponse;
  formalParseTree: WasteQueryTreeNodeResponse;
  tokens: TokenInfoResponse[];
  result: string;
  queryAction: string;
  engineUsed: string;
  decisionReason: string;
  primaryResult: WasteEngineResultResponse | null;
  fallbackResult: WasteEngineResultResponse | null;
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
  const engine = response.engine_used === "custom_waste_detector" ? "custom model" : "COCO fallback";
  const count = response.match_count;

  if (count === 0) {
    return `No ${targetGroup} items matched "${response.normalized_query}" via ${engine}.`;
  }

  const labelFilter = response.label_filter
    ? ` with label "${response.label_filter}"`
    : "";
  const confidenceFilter =
    response.minimum_confidence !== null &&
    response.minimum_confidence !== undefined &&
    response.confidence_operator
      ? ` confidence ${response.confidence_operator} ${response.minimum_confidence}`
      : "";
  const filters = [labelFilter, confidenceFilter].filter(Boolean).join(",");

  if (action === "count") {
    return `Counted ${count} ${targetGroup} item(s)${filters} via ${engine}.`;
  }
  return `Found ${count} ${targetGroup} item(s)${filters} via ${engine}.`;
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

  const classify = async (file: File, query: string, useSahi: boolean = false) => {
    setLoading(true);
    setError(null);

    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
    }

    const imageUrl = URL.createObjectURL(file);
    objectUrlRef.current = imageUrl;

    try {
      const response = await findWaste(file, query, useSahi);

      setData({
        imageUrl,
        detectedObjects: mapDetectionsToDetectedObjects(response.detections, response),
        matchedObjects: mapDetectionsToDetectedObjects(response.matches, response),
        dslCode: response.normalized_query,
        parseTree: response.parse_tree,
        formalParseTree: response.formal_parse_tree,
        tokens: response.tokens,
        result: buildResultSummary(response),
        queryAction: response.query_action,
        engineUsed: response.engine_used,
        decisionReason: response.decision_reason,
        primaryResult: response.primary_result ?? null,
        fallbackResult: response.fallback_result ?? null,
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
