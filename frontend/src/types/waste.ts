export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
}

export interface DetectionObject {
  class_id: number;
  label: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface ImageMetadata {
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

export interface DetectionSummary {
  total_detections: number;
  unique_labels: string[];
  class_counts: Record<string, number>;
  confidence_threshold: number;
  iou_threshold: number;
  inference_ms: number;
}

export interface DetectionResponse {
  model: ModelStatusResponse;
  image: ImageMetadata;
  detections: DetectionObject[];
  summary: DetectionSummary;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  model: ModelStatusResponse;
}
