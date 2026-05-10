from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.api.deps import get_detector, get_hybrid_waste_detector, get_settings
from app.core.config import Settings
from app.main import create_application
from app.schemas.waste import HybridWasteModelsResponse, WasteFindResponse
from app.schemas.yolov26 import (
    BoundingBox,
    DetectionObject,
    DetectionResponse,
    DetectionSummary,
    ImageMetadata,
    ModelStatusResponse,
)
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


class FakeHybridDetector:
    @staticmethod
    def get_models_status() -> HybridWasteModelsResponse:
        model = ModelStatusResponse(
            name="waste_yolo26s_taco",
            weights_path="runs/waste_detector/waste_yolo26s_taco/weights/best.pt",
            weights_present=True,
            model_loaded=True,
            device="cpu",
            image_size=640,
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=100,
            preload_on_startup=False,
        )
        fallback_model = ModelStatusResponse(
            name="yolo26n",
            weights_path="runtime/weights/yolo26n.pt",
            weights_present=True,
            model_loaded=True,
            device="cpu",
            image_size=640,
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=100,
            preload_on_startup=False,
        )
        return HybridWasteModelsResponse(
            primary_engine="custom_waste_detector",
            fallback_engine="coco_rule_map",
            primary_model=model,
            fallback_model=fallback_model,
            primary_min_confidence=0.45,
            primary_min_matches=1,
        )

    def find(
        self,
        *,
        query: str,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
    ) -> WasteFindResponse:
        result_model = self.get_models_status().primary_model
        image = ImageMetadata(
            filename=filename or "sample.png",
            content_type=content_type or "image/png",
            size_bytes=len(image_bytes),
            sha256="c" * 64,
            width=20,
            height=20,
            format="PNG",
        )
        detections = [
            DetectionObject(
                class_id=1,
                label="recyclable",
                confidence=0.88,
                bbox=BoundingBox(x1=1, y1=2, x2=11, y2=18, width=10, height=16),
            )
        ]
        summary = DetectionSummary(
            total_detections=1,
            unique_labels=["recyclable"],
            class_counts={"recyclable": 1},
            confidence_threshold=0.25,
            iou_threshold=0.45,
            inference_ms=3.21,
        )
        engine_result = {
            "engine": "custom_waste_detector",
            "model": result_model,
            "image": image,
            "detections": detections,
            "summary": summary,
            "matches": detections,
            "match_count": 1,
            "max_match_confidence": 0.88,
        }
        return WasteFindResponse(
            model=result_model,
            image=image,
            detections=detections,
            summary=summary,
            raw_query=query,
            normalized_query="find recyclable waste",
            query_action="find",
            waste_group="recyclable",
            targets=["bottle"],
            tokens=[],
            parse_tree={
                "name": "WasteQuery",
                "children": [
                    {"name": "Action", "children": [{"name": "find"}]},
                    {"name": "WasteGroup", "children": [{"name": "recyclable"}]},
                ],
            },
            formal_parse_tree={"name": "query", "is_terminal": False},
            confidence_operator=None,
            minimum_confidence=None,
            label_filter=None,
            matches=detections,
            match_count=1,
            engine_used="custom_waste_detector",
            decision_reason="Primary waste detector matched the requested group with sufficient confidence.",
            primary_result=engine_result,
            fallback_result=None,
            primary_error=None,
            fallback_error=None,
        )



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



def test_waste_query_routes_report_supported_queries() -> None:
    app = create_application()
    client = TestClient(app)

    response = client.get("/api/v1/waste/queries")

    assert response.status_code == 200
    payload = response.json()
    assert "organic" in payload["supported_groups"]
    assert "find me recyclable waste" in payload["supported_queries"]
    assert "count organic waste where confidence >= 0.6" in payload["dsl_examples"]
    assert "bottle" in payload["group_keywords"]["recyclable"]



def test_waste_models_route_reports_hybrid_status() -> None:
    app = create_application()
    app.dependency_overrides[get_hybrid_waste_detector] = lambda: FakeHybridDetector()
    client = TestClient(app)

    response = client.get("/api/v1/waste/models")

    payload = response.json()
    assert response.status_code == 200
    assert payload["primary_engine"] == "custom_waste_detector"
    assert payload["fallback_engine"] == "coco_rule_map"



def test_waste_find_route_returns_hybrid_payload() -> None:
    app = create_application()
    app.dependency_overrides[get_hybrid_waste_detector] = lambda: FakeHybridDetector()
    client = TestClient(app)

    response = client.post(
        "/api/v1/waste/find",
        data={"query": "find me recyclable waste"},
        files={"file": ("sample.png", make_png_bytes(), "image/png")},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["waste_group"] == "recyclable"
    assert payload["query_action"] == "find"
    assert payload["engine_used"] == "custom_waste_detector"
    assert payload["match_count"] == 1
    assert payload["parse_tree"]["name"] == "WasteQuery"
    assert payload["matches"][0]["label"] == "recyclable"
