class YoloBackendError(Exception):
    """Base exception for YOLOv26 backend errors."""


class InvalidImageError(YoloBackendError):
    """Raised when an uploaded file fails image validation."""


class ModelNotConfiguredError(YoloBackendError):
    """Raised when model weights or runtime dependencies are unavailable."""


class InferenceError(YoloBackendError):
    """Raised when model inference output cannot be produced safely."""
