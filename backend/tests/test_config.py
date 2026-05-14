from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import BACKEND_DIR, Settings



def test_resolved_weights_paths_are_backend_relative() -> None:
    settings = Settings(
        yolov26_weights_path=Path("runtime/weights/custom.pt"),
        waste_detector_weights_path=Path("runs/waste_detector/custom/best.pt"),
    )
    assert settings.resolved_weights_path == BACKEND_DIR / "runtime/weights/custom.pt"
    assert settings.resolved_waste_detector_weights_path == BACKEND_DIR / "runs/waste_detector/custom/best.pt"



def test_settings_parse_csv_lists() -> None:
    settings = Settings(
        allowed_image_types="image/png, image/jpeg",
        cors_origins="http://localhost:5173, https://example.com",
    )

    assert settings.allowed_image_type_list == ["image/png", "image/jpeg"]
    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "https://example.com",
    ]


def test_settings_parse_hybrid_configuration() -> None:
    settings = Settings(
        hybrid_weak_groups="organic, recyclable",
        hybrid_group_min_confidence="recyclable=0.40, inorganic=0.35",
        hybrid_strategy="MERGE",
    )

    assert settings.weak_group_list == ["organic", "recyclable"]
    assert settings.group_confidence_overrides == {
        "recyclable": 0.40,
        "inorganic": 0.35,
    }
    assert settings.hybrid_strategy == "merge"


def test_settings_reject_invalid_hybrid_strategy() -> None:
    with pytest.raises(ValidationError, match="hybrid_strategy"):
        Settings(hybrid_strategy="balanced")
