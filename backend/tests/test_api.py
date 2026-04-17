from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.api.deps import get_detector, get_settings
from app.core.config import Settings
from app.main import create_application
from app.services.yolov26_detector import YoloV26Detector



def make_png_bytes() -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (20, 20), color=(255, 120, 0))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class FakeBox:
    def __init__(self, xyxy: list[float], confidence: float, class_id: int) -> None:
        self.xyxy = [xyxy]
        self.conf = [confidence]
        self.cls = [class_id]


class FakeResult:
    def __init__(self) -> None:
        self.names = {0: "bottle"}
        self.boxes = [FakeBox([1.0, 2.0, 11.0, 18.0], 0.91, 0)]


class FakeModel:
    def predict(self, **kwargs):
        return [FakeResult()]



def test_health_and_model_routes_report_detector_state(tmp_path: Path) -> None:
    settings = Settings(
        yolov26_weights_path=tmp_path / "missing.pt",
        allowed_image_types="image/png",
    )
    detector = YoloV26Detector(settings=settings, model_factory=lambda _: FakeModel())

    app = create_application()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_detector] = lambda: detector
    client = TestClient(app)

    health_response = client.get("/api/v1/healthz")
    model_response = client.get("/api/v1/yolov26/model")

    assert health_response.status_code == 200
    assert health_response.json()["model"]["weights_present"] is False
    assert model_response.status_code == 200
    assert model_response.json()["model_loaded"] is False



def test_detect_route_returns_structured_detection_payload(tmp_path: Path) -> None:
    weights_path = tmp_path / "yolo26n.pt"
    weights_path.write_text("placeholder", encoding="utf-8")

    settings = Settings(
        yolov26_weights_path=weights_path,
        allowed_image_types="image/png",
    )
    detector = YoloV26Detector(settings=settings, model_factory=lambda _: FakeModel())

    app = create_application()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_detector] = lambda: detector
    client = TestClient(app)

    response = client.post(
        "/api/v1/yolov26/detect",
        files={"file": ("sample.png", make_png_bytes(), "image/png")},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["detections"][0]["label"] == "bottle"
    assert payload["summary"]["total_detections"] == 1
    assert payload["image"]["content_type"] == "image/png"
