from __future__ import annotations

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float = Field(..., ge=0)
    y1: float = Field(..., ge=0)
    x2: float = Field(..., ge=0)
    y2: float = Field(..., ge=0)
    width: float = Field(..., ge=0)
    height: float = Field(..., ge=0)


class DetectionObject(BaseModel):
    class_id: int = Field(..., ge=0)
    label: str
    confidence: float = Field(..., ge=0, le=1)
    bbox: BoundingBox


class ImageMetadata(BaseModel):
    filename: str
    content_type: str
    size_bytes: int = Field(..., ge=0)
    sha256: str
    width: int = Field(..., ge=1)
    height: int = Field(..., ge=1)
    format: str


class ModelStatusResponse(BaseModel):
    name: str
    weights_path: str
    weights_present: bool
    model_loaded: bool
    device: str
    image_size: int = Field(..., ge=1)
    confidence_threshold: float = Field(..., gt=0, le=1)
    iou_threshold: float = Field(..., gt=0, le=1)
    max_detections: int = Field(..., ge=1)
    preload_on_startup: bool


class DetectionSummary(BaseModel):
    total_detections: int = Field(..., ge=0)
    unique_labels: list[str]
    class_counts: dict[str, int]
    confidence_threshold: float = Field(..., gt=0, le=1)
    iou_threshold: float = Field(..., gt=0, le=1)
    inference_ms: float = Field(..., ge=0)


class DetectionResponse(BaseModel):
    model: ModelStatusResponse
    image: ImageMetadata
    detections: list[DetectionObject]
    summary: DetectionSummary


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model: ModelStatusResponse
