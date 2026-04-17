from io import BytesIO

import pytest
from PIL import Image

from app.core.config import Settings
from app.core.errors import InvalidImageError
from app.services.image_validation import validate_uploaded_image



def make_png_bytes() -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (8, 8), color=(10, 160, 90))
    image.save(buffer, format="PNG")
    return buffer.getvalue()



def test_validate_uploaded_image_accepts_png() -> None:
    settings = Settings(allowed_image_types="image/png", upload_max_bytes=1024 * 1024)

    validated = validate_uploaded_image(
        filename="sample.png",
        content_type="image/png",
        image_bytes=make_png_bytes(),
        settings=settings,
    )

    assert validated.filename == "sample.png"
    assert validated.content_type == "image/png"
    assert validated.width == 8
    assert validated.height == 8
    assert validated.format == "PNG"
    assert len(validated.sha256) == 64



def test_validate_uploaded_image_rejects_wrong_content_type() -> None:
    settings = Settings(allowed_image_types="image/png")

    with pytest.raises(InvalidImageError, match="Unsupported content type"):
        validate_uploaded_image(
            filename="sample.png",
            content_type="image/jpeg",
            image_bytes=make_png_bytes(),
            settings=settings,
        )



def test_validate_uploaded_image_rejects_large_payload() -> None:
    settings = Settings(allowed_image_types="image/png", upload_max_bytes=10)

    with pytest.raises(InvalidImageError, match="larger than the configured limit"):
        validate_uploaded_image(
            filename="sample.png",
            content_type="image/png",
            image_bytes=make_png_bytes(),
            settings=settings,
        )
