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

    waste_detector_model_name: str = "waste_yolo26s_taco"
    waste_detector_weights_path: Path = Path("runs/waste_detector/waste_yolo26s_taco/weights/best.pt")
    waste_detector_confidence_threshold: float = 0.25
    waste_detector_iou_threshold: float = 0.45
    waste_detector_image_size: PositiveInt = 640
    waste_detector_max_detections: PositiveInt = 100
    waste_detector_device: str = "cpu"
    waste_detector_preload_on_startup: bool = False

    hybrid_primary_min_confidence: float = 0.45
    hybrid_primary_min_matches: PositiveInt = 1
    # Groups listed here always skip the primary model and go straight to the COCO fallback.
    # Default: "organic" because the TACO training set has fewer than 10 organic boxes,
    # making primary predictions unreliable for that group.
    hybrid_weak_groups: str = "organic"
    # Per-group confidence overrides. Format: "group=threshold,group=threshold"
    # Example: "recyclable=0.40,inorganic=0.35"
    # Groups not listed fall back to hybrid_primary_min_confidence.
    hybrid_group_min_confidence: str = ""
    # Detection strategy: "fallback" (primary-then-fallback) or "merge" (spatial NMS blend).
    hybrid_strategy: str = "fallback"
    # Enable Test-Time Augmentation (horizontal flip + scale) for the primary waste detector.
    # Improves recall ~5–10% at the cost of ~2× inference time.
    detector_use_tta: bool = False

    @field_validator(
        "yolov26_confidence_threshold",
        "yolov26_iou_threshold",
        "waste_detector_confidence_threshold",
        "waste_detector_iou_threshold",
        "hybrid_primary_min_confidence",
    )
    @classmethod
    def validate_thresholds(cls, value: float) -> float:
        if not 0 < value <= 1:
            raise ValueError("Threshold values must be between 0 and 1.")
        return value

    @field_validator("hybrid_strategy")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        allowed = {"fallback", "merge"}
        if value.lower() not in allowed:
            raise ValueError(f"hybrid_strategy must be one of {allowed}.")
        return value.lower()

    @property
    def resolved_weights_path(self) -> Path:
        if self.yolov26_weights_path.is_absolute():
            return self.yolov26_weights_path
        return BACKEND_DIR / self.yolov26_weights_path

    @property
    def resolved_waste_detector_weights_path(self) -> Path:
        if self.waste_detector_weights_path.is_absolute():
            return self.waste_detector_weights_path
        return BACKEND_DIR / self.waste_detector_weights_path

    @property
    def weak_group_list(self) -> list[str]:
        return [g.strip().lower() for g in self.hybrid_weak_groups.split(",") if g.strip()]

    @property
    def group_confidence_overrides(self) -> dict[str, float]:
        """Parse WASTE_HYBRID_GROUP_MIN_CONFIDENCE into a dict[group -> threshold]."""
        overrides: dict[str, float] = {}
        for entry in self.hybrid_group_min_confidence.split(","):
            entry = entry.strip()
            if "=" not in entry:
                continue
            group, _, raw_val = entry.partition("=")
            try:
                overrides[group.strip().lower()] = float(raw_val.strip())
            except ValueError:
                pass
        return overrides

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
