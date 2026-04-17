from __future__ import annotations

from collections import Counter
from threading import Lock
from time import perf_counter
from typing import Any, Callable

from app.core.config import Settings
from app.core.errors import InferenceError, ModelNotConfiguredError
from app.schemas.yolov26 import (
    BoundingBox,
    DetectionObject,
    DetectionResponse,
    DetectionSummary,
    ImageMetadata,
    ModelStatusResponse,
)
from app.services.image_validation import validate_uploaded_image

ModelFactory = Callable[[str], Any]


class YoloV26Detector:
    def __init__(
        self,
        *,
        settings: Settings,
        model_factory: ModelFactory | None = None,
    ) -> None:
        self._settings = settings
        self._model_factory = model_factory
        self._model: Any | None = None
        self._model_lock = Lock()

    def preload(self) -> None:
        self._load_model()

    def get_model_status(self) -> ModelStatusResponse:
        weights_path = self._settings.resolved_weights_path
        return ModelStatusResponse(
            name=self._settings.yolov26_model_name,
            weights_path=str(weights_path),
            weights_present=weights_path.exists(),
            model_loaded=self._model is not None,
            device=self._settings.yolov26_device,
            image_size=self._settings.yolov26_image_size,
            confidence_threshold=self._settings.yolov26_confidence_threshold,
            iou_threshold=self._settings.yolov26_iou_threshold,
            max_detections=self._settings.yolov26_max_detections,
            preload_on_startup=self._settings.yolov26_preload_on_startup,
        )

    def detect(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
    ) -> DetectionResponse:
        validated_image = validate_uploaded_image(
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
            settings=self._settings,
        )
        model = self._load_model()

        started_at = perf_counter()
        try:
            results = model.predict(
                source=validated_image.image,
                conf=self._settings.yolov26_confidence_threshold,
                iou=self._settings.yolov26_iou_threshold,
                imgsz=self._settings.yolov26_image_size,
                device=self._settings.yolov26_device,
                max_det=self._settings.yolov26_max_detections,
                verbose=False,
            )
        except Exception as exc:
            raise InferenceError(f"YOLOv26 inference failed: {exc}") from exc

        detections = self._serialize_detections(results)
        class_counts = dict(Counter(detection.label for detection in detections))

        return DetectionResponse(
            model=self.get_model_status(),
            image=ImageMetadata(
                filename=validated_image.filename,
                content_type=validated_image.content_type,
                size_bytes=validated_image.size_bytes,
                sha256=validated_image.sha256,
                width=validated_image.width,
                height=validated_image.height,
                format=validated_image.format,
            ),
            detections=detections,
            summary=DetectionSummary(
                total_detections=len(detections),
                unique_labels=sorted(class_counts),
                class_counts=class_counts,
                confidence_threshold=self._settings.yolov26_confidence_threshold,
                iou_threshold=self._settings.yolov26_iou_threshold,
                inference_ms=round((perf_counter() - started_at) * 1000, 2),
            ),
        )

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is not None:
                return self._model

            weights_path = self._settings.resolved_weights_path
            if not weights_path.exists():
                raise ModelNotConfiguredError(
                    "YOLOv26 weights were not found at "
                    f"'{weights_path}'. Configure WASTE_YOLOV26_WEIGHTS_PATH first."
                )

            factory = self._model_factory or self._default_model_factory
            try:
                self._model = factory(str(weights_path))
            except Exception as exc:
                raise ModelNotConfiguredError(
                    "Failed to load YOLOv26 weights from "
                    f"'{weights_path}': {exc}"
                ) from exc

        return self._model

    @staticmethod
    def _default_model_factory(weights_path: str) -> Any:
        try:
            from ultralytics import YOLO
        except Exception as exc:
            raise ModelNotConfiguredError(
                "The 'ultralytics' package is not installed in this environment."
            ) from exc
        return YOLO(weights_path)

    def _serialize_detections(self, results: Any) -> list[DetectionObject]:
        detections: list[DetectionObject] = []

        for result in results or []:
            names = self._extract_names(result)
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            for box in boxes:
                coordinates = self._as_list(self._first(getattr(box, "xyxy", [])))
                if len(coordinates) != 4:
                    raise InferenceError("YOLOv26 returned an invalid bounding box.")

                class_id = int(self._as_scalar(getattr(box, "cls", 0)))
                confidence = round(float(self._as_scalar(getattr(box, "conf", 0.0))), 4)
                x1, y1, x2, y2 = [round(float(value), 2) for value in coordinates]

                detections.append(
                    DetectionObject(
                        class_id=class_id,
                        label=names.get(class_id, str(class_id)),
                        confidence=confidence,
                        bbox=BoundingBox(
                            x1=x1,
                            y1=y1,
                            x2=x2,
                            y2=y2,
                            width=round(max(x2 - x1, 0.0), 2),
                            height=round(max(y2 - y1, 0.0), 2),
                        ),
                    )
                )

        detections.sort(key=lambda detection: detection.confidence, reverse=True)
        return detections

    def _extract_names(self, result: Any) -> dict[int, str]:
        raw_names = getattr(result, "names", None)
        if raw_names is None and self._model is not None:
            raw_names = getattr(self._model, "names", None)

        if isinstance(raw_names, dict):
            return {int(class_id): str(name) for class_id, name in raw_names.items()}

        if isinstance(raw_names, (list, tuple)):
            return {index: str(name) for index, name in enumerate(raw_names)}

        return {}

    @staticmethod
    def _first(value: Any) -> Any:
        if isinstance(value, (list, tuple)):
            return value[0] if value else []
        return value

    @classmethod
    def _as_scalar(cls, value: Any) -> Any:
        current = value
        while isinstance(current, (list, tuple)):
            if not current:
                return 0
            current = current[0]

        if hasattr(current, "item"):
            current = current.item()

        return current

    @classmethod
    def _as_list(cls, value: Any) -> list[float]:
        current = value
        if hasattr(current, "tolist"):
            current = current.tolist()

        if isinstance(current, (list, tuple)):
            return [float(item) for item in current]

        raise InferenceError("YOLOv26 returned a non-serializable bounding box.")
