from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.config import Settings
from app.core.errors import InvalidImageError


@dataclass(slots=True)
class ValidatedImage:
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    width: int
    height: int
    format: str
    image: Image.Image



def validate_uploaded_image(
    *,
    filename: str | None,
    content_type: str | None,
    image_bytes: bytes,
    settings: Settings,
) -> ValidatedImage:
    safe_filename = Path(filename or "upload").name or "upload"
    normalized_content_type = (content_type or "").lower().strip()

    if not image_bytes:
        raise InvalidImageError("Uploaded file is empty.")

    if len(image_bytes) > settings.upload_max_bytes:
        raise InvalidImageError(
            "Uploaded file is larger than the configured limit of "
            f"{settings.upload_max_bytes} bytes."
        )

    if normalized_content_type not in settings.allowed_image_type_list:
        raise InvalidImageError(
            "Unsupported content type. Allowed values are: "
            f"{', '.join(settings.allowed_image_type_list)}."
        )

    try:
        with Image.open(BytesIO(image_bytes)) as raw_image:
            raw_image.load()
            rgb_image = raw_image.convert("RGB")
            width, height = rgb_image.size
            image_format = (raw_image.format or "UNKNOWN").upper()
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("Uploaded file is not a valid image.") from exc

    if width < 1 or height < 1:
        raise InvalidImageError("Uploaded image has invalid dimensions.")

    return ValidatedImage(
        filename=safe_filename,
        content_type=normalized_content_type,
        size_bytes=len(image_bytes),
        sha256=sha256(image_bytes).hexdigest(),
        width=width,
        height=height,
        format=image_format,
        image=rgb_image,
    )
