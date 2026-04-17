from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from app.core.config import Settings
from app.core.errors import ModelNotConfiguredError
from app.services.yolov26_detector import YoloV26Detector



def make_png_bytes() -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (16, 12), color=(40, 100, 220))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class FakeBox:
    def __init__(self, xyxy: list[float], confidence: float, class_id: int) -> None:
        self.xyxy = [xyxy]
        self.conf = [confidence]
        self.cls = [class_id]


class FakeResult:
    def __init__(self) -> None:
        self.names = {0: "bottle", 1: "banana"}
        self.boxes = [
            FakeBox([10.0, 20.0, 110.0, 220.0], 0.83, 0),
            FakeBox([5.0, 15.0, 55.0, 85.0], 0.62, 1),
        ]


class FakeModel:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def predict(self, **kwargs):
        self.calls.append(kwargs)
        return [FakeResult()]



def test_detect_serializes_ultralytics_style_output(tmp_path: Path) -> None:
    weights_path = tmp_path / "yolo26n.pt"
    weights_path.write_text("placeholder", encoding="utf-8")

    fake_model = FakeModel()
    settings = Settings(
        yolov26_weights_path=weights_path,
        allowed_image_types="image/png",
        yolov26_confidence_threshold=0.2,
        yolov26_iou_threshold=0.4,
        yolov26_image_size=640,
    )
    detector = YoloV26Detector(
        settings=settings,
        model_factory=lambda supplied_path: fake_model
        if supplied_path == str(weights_path)
        else None,
    )

    response = detector.detect(
        filename="sample.png",
        content_type="image/png",
        image_bytes=make_png_bytes(),
    )

    assert response.summary.total_detections == 2
    assert response.summary.class_counts == {"banana": 1, "bottle": 1}
    assert response.detections[0].label == "bottle"
    assert response.detections[0].bbox.width == 100.0
    assert response.detections[0].bbox.height == 200.0
    assert response.model.model_loaded is True
    assert fake_model.calls[0]["imgsz"] == 640
    assert fake_model.calls[0]["device"] == "cpu"



def test_detector_requires_existing_weights(tmp_path: Path) -> None:
    settings = Settings(
        yolov26_weights_path=tmp_path / "missing.pt",
        allowed_image_types="image/png",
    )
    detector = YoloV26Detector(settings=settings, model_factory=lambda _: object())

    with pytest.raises(ModelNotConfiguredError, match="weights were not found"):
        detector.detect(
            filename="sample.png",
            content_type="image/png",
            image_bytes=make_png_bytes(),
        )
