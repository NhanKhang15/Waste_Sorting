export interface BoundingBoxResponse {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
}

export interface DetectionObjectResponse {
  class_id: number;
  label: string;
  confidence: number;
  bbox: BoundingBoxResponse;
}

export interface ImageMetadataResponse {
  filename: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
  width: number;
  height: number;
  format: string;
}

export interface ModelStatusResponse {
  name: string;
  weights_path: string;
  weights_present: boolean;
  model_loaded: boolean;
  device: string;
  image_size: number;
  confidence_threshold: number;
  iou_threshold: number;
  max_detections: number;
  preload_on_startup: boolean;
}

export interface DetectionSummaryResponse {
  total_detections: number;
  unique_labels: string[];
  class_counts: Record<string, number>;
  confidence_threshold: number;
  iou_threshold: number;
  inference_ms: number;
}

export interface YoloDetectionResponse {
  model: ModelStatusResponse;
  image: ImageMetadataResponse;
  detections: DetectionObjectResponse[];
  summary: DetectionSummaryResponse;
}

export interface WasteQueryTreeNodeResponse {
  name: string;
  children: WasteQueryTreeNodeResponse[];
}

export interface WasteFindResponse {
  model: ModelStatusResponse;
  image: ImageMetadataResponse;
  detections: DetectionObjectResponse[];
  summary: DetectionSummaryResponse;
  raw_query: string;
  normalized_query: string;
  query_action: string;
  waste_group: string;
  targets: string[];
  parse_tree: WasteQueryTreeNodeResponse;
  confidence_operator?: string | null;
  minimum_confidence?: number | null;
  label_filter?: string | null;
  matches: DetectionObjectResponse[];
  match_count: number;
  engine_used: string;
  decision_reason: string;
}
