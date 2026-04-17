from pathlib import Path

from app.core.config import BACKEND_DIR, Settings



def test_resolved_weights_path_is_backend_relative() -> None:
    settings = Settings(yolov26_weights_path=Path("runtime/weights/custom.pt"))
    assert settings.resolved_weights_path == BACKEND_DIR / "runtime/weights/custom.pt"



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
