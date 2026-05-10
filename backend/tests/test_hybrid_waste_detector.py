from __future__ import annotations

from io import BytesIO

from PIL import Image

from app.core.config import Settings
from app.schemas.yolov26 import (
    BoundingBox,
    DetectionObject,
    DetectionResponse,
    DetectionSummary,
    ImageMetadata,
    ModelStatusResponse,
)
from app.services.hybrid_waste_detector import HybridWasteDetector
from app.services.waste_rules import WasteRuleMatcher



def make_png_bytes() -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (16, 12), color=(40, 100, 220))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class FakeDetector:
    def __init__(self, response: DetectionResponse) -> None:
        self._response = response

    def get_model_status(self) -> ModelStatusResponse:
        return self._response.model

    def detect(self, *, filename: str | None, content_type: str | None, image_bytes: bytes) -> DetectionResponse:
        return self._response



def make_response(labels: list[tuple[str, float]]) -> DetectionResponse:
    detections = []
    for index, (label, confidence) in enumerate(labels):
        detections.append(
            DetectionObject(
                class_id=index,
                label=label,
                confidence=confidence,
                bbox=BoundingBox(x1=1, y1=2, x2=10, y2=12, width=9, height=10),
            )
        )

    model = ModelStatusResponse(
        name="model",
        weights_path="weights.pt",
        weights_present=True,
        model_loaded=True,
        device="cpu",
        image_size=640,
        confidence_threshold=0.25,
        iou_threshold=0.45,
        max_detections=100,
        preload_on_startup=False,
    )
    image = ImageMetadata(
        filename="sample.png",
        content_type="image/png",
        size_bytes=123,
        sha256="d" * 64,
        width=16,
        height=12,
        format="PNG",
    )
    summary = DetectionSummary(
        total_detections=len(detections),
        unique_labels=sorted({detection.label for detection in detections}),
        class_counts={label: sum(1 for detection in detections if detection.label == label) for label, _ in labels},
        confidence_threshold=0.25,
        iou_threshold=0.45,
        inference_ms=5.43,
    )
    return DetectionResponse(
        model=model,
        image=image,
        detections=detections,
        summary=summary,
    )



def test_hybrid_uses_primary_when_match_is_confident() -> None:
    settings = Settings(
        allowed_image_types="image/png",
        waste_hybrid_primary_min_confidence=0.45,
    )
    hybrid = HybridWasteDetector(
        settings=settings,
        primary_detector=FakeDetector(make_response([("recyclable", 0.88)])),
        fallback_detector=FakeDetector(make_response([("bottle", 0.91)])),
        matcher=WasteRuleMatcher(),
    )

    response = hybrid.find(
        query="find me recyclable waste",
        filename="sample.png",
        content_type="image/png",
        image_bytes=make_png_bytes(),
    )

    assert response.engine_used == "custom_waste_detector"
    assert response.match_count == 1
    assert response.fallback_result is None
    assert response.matches[0].label == "recyclable"



def test_hybrid_falls_back_when_primary_confidence_is_too_low() -> None:
    settings = Settings(
        allowed_image_types="image/png",
        waste_hybrid_primary_min_confidence=0.45,
    )
    hybrid = HybridWasteDetector(
        settings=settings,
        primary_detector=FakeDetector(make_response([("recyclable", 0.20)])),
        fallback_detector=FakeDetector(make_response([("bottle", 0.91)])),
        matcher=WasteRuleMatcher(),
    )

    response = hybrid.find(
        query="find me recyclable waste",
        filename="sample.png",
        content_type="image/png",
        image_bytes=make_png_bytes(),
    )

    assert response.engine_used == "coco_rule_map"
    assert response.primary_result is not None
    assert response.fallback_result is not None
    assert response.matches[0].label == "bottle"
    assert "confidence threshold" in response.decision_reason
