from __future__ import annotations

from pathlib import Path

from pydantic import PositiveInt, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WASTE_",
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Waste Sorting YOLOv26 Backend"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    cors_origins: str = ""
    upload_max_bytes: PositiveInt = 8 * 1024 * 1024
    allowed_image_types: str = "image/jpeg,image/png,image/webp"

    yolov26_model_name: str = "yolo26n"
    yolov26_weights_path: Path = Path("runtime/weights/yolo26n.pt")
    yolov26_confidence_threshold: float = 0.25
    yolov26_iou_threshold: float = 0.45
    yolov26_image_size: PositiveInt = 640
    yolov26_max_detections: PositiveInt = 100
    yolov26_device: str = "cpu"
    yolov26_preload_on_startup: bool = False

    @field_validator("yolov26_confidence_threshold", "yolov26_iou_threshold")
    @classmethod
    def validate_thresholds(cls, value: float) -> float:
        if not 0 < value <= 1:
            raise ValueError("Threshold values must be between 0 and 1.")
        return value

    @property
    def resolved_weights_path(self) -> Path:
        if self.yolov26_weights_path.is_absolute():
            return self.yolov26_weights_path
        return BACKEND_DIR / self.yolov26_weights_path

    @property
    def allowed_image_type_list(self) -> list[str]:
        return [
            image_type.strip().lower()
            for image_type in self.allowed_image_types.split(",")
            if image_type.strip()
        ]

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
