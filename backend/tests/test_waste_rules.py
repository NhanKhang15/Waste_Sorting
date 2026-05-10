from app.core.errors import InvalidWasteQueryError
from app.schemas.yolov26 import (
    BoundingBox,
    DetectionObject,
    DetectionResponse,
    DetectionSummary,
    ImageMetadata,
    ModelStatusResponse,
)
from app.services.waste_rules import WasteRuleMatcher


def make_detection_response() -> DetectionResponse:
    return DetectionResponse(
        model=ModelStatusResponse(
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
        ),
        image=ImageMetadata(
            filename="sample.png",
            content_type="image/png",
            size_bytes=128,
            sha256="a" * 64,
            width=64,
            height=64,
            format="PNG",
        ),
        detections=[
            DetectionObject(
                class_id=0,
                label="bottle",
                confidence=0.91,
                bbox=BoundingBox(
                    x1=1,
                    y1=2,
                    x2=20,
                    y2=30,
                    width=19,
                    height=28,
                ),
            ),
            DetectionObject(
                class_id=1,
                label="banana",
                confidence=0.83,
                bbox=BoundingBox(
                    x1=5,
                    y1=6,
                    x2=24,
                    y2=40,
                    width=19,
                    height=34,
                ),
            ),
            DetectionObject(
                class_id=2,
                label="recyclable",
                confidence=0.77,
                bbox=BoundingBox(
                    x1=10,
                    y1=12,
                    x2=42,
                    y2=46,
                    width=32,
                    height=34,
                ),
            ),
        ],
        summary=DetectionSummary(
            total_detections=3,
            unique_labels=["banana", "bottle", "recyclable"],
            class_counts={"banana": 1, "bottle": 1, "recyclable": 1},
            confidence_threshold=0.25,
            iou_threshold=0.45,
            inference_ms=12.34,
        ),
    )


def test_match_detections_filters_by_supported_group() -> None:
    matcher = WasteRuleMatcher()

    parsed_query, matches = matcher.match_detections(
        query="find me recyclable waste",
        response=make_detection_response(),
    )

    assert parsed_query.waste_group == "recyclable"
    assert parsed_query.query_action == "find"
    assert "bottle" in parsed_query.allowed_keywords
    assert parsed_query.normalized_query == "find recyclable waste"
    assert parsed_query.parse_tree["name"] == "WasteQuery"
    assert [match.label for match in matches] == ["bottle", "recyclable"]


def test_classify_label_accepts_direct_group_names() -> None:
    matcher = WasteRuleMatcher()
    assert matcher.classify_label("recyclable") == "recyclable"


def test_match_detections_respects_confidence_filter() -> None:
    matcher = WasteRuleMatcher()

    parsed_query, matches = matcher.match_detections(
        query="find recyclable waste where confidence >= 0.8",
        response=make_detection_response(),
    )

    assert parsed_query.confidence_operator == ">="
    assert parsed_query.minimum_confidence == 0.8
    assert [match.label for match in matches] == ["bottle"]


def test_match_detections_respects_label_filter_and_count_action() -> None:
    matcher = WasteRuleMatcher()

    parsed_query, matches = matcher.match_detections(
        query="count recyclable waste where label = bottle",
        response=make_detection_response(),
    )

    assert parsed_query.query_action == "count"
    assert parsed_query.label_filter == "bottle"
    assert [match.label for match in matches] == ["bottle"]


def test_parse_query_rejects_unknown_values() -> None:
    matcher = WasteRuleMatcher()

    try:
        matcher.parse_query("find me hazardous waste")
    except InvalidWasteQueryError as exc:
        assert "Unsupported DSL query" in str(exc)
    else:
        raise AssertionError("InvalidWasteQueryError was not raised")
