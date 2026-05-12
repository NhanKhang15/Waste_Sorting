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
        weights_path = self._weights_path
        return ModelStatusResponse(
            name=self._model_name,
            weights_path=str(weights_path),
            weights_present=weights_path.exists(),
            model_loaded=self._model is not None,
            device=self._device,
            image_size=self._image_size,
            confidence_threshold=self._confidence_threshold,
            iou_threshold=self._iou_threshold,
            max_detections=self._max_detections,
            preload_on_startup=self._preload_on_startup,
        )

    def detect(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
        use_slicing: bool = False,
        slice_width: int = 640,
        slice_height: int = 640,
        overlap_ratio: float = 0.2,
        postprocess_iou_threshold: float = 0.5,
    ) -> DetectionResponse:
        if use_slicing:
            return self._detect_sliced(
                filename=filename,
                content_type=content_type,
                image_bytes=image_bytes,
                slice_width=slice_width,
                slice_height=slice_height,
                overlap_ratio=overlap_ratio,
                postprocess_iou_threshold=postprocess_iou_threshold,
            )
        return self._detect_full(
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
        )

    def _detect_full(
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
                conf=self._confidence_threshold,
                iou=self._iou_threshold,
                imgsz=self._image_size,
                device=self._device,
                max_det=self._max_detections,
                augment=self._augment,
                verbose=False,
            )
        except Exception as exc:
            raise InferenceError(f"{self._model_name} inference failed: {exc}") from exc

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
                confidence_threshold=self._confidence_threshold,
                iou_threshold=self._iou_threshold,
                inference_ms=round((perf_counter() - started_at) * 1000, 2),
            ),
        )

    def _detect_sliced(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
        slice_width: int,
        slice_height: int,
        overlap_ratio: float,
        postprocess_iou_threshold: float,
    ) -> DetectionResponse:
        validated_image = validate_uploaded_image(
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
            settings=self._settings,
        )
        model = self._load_model()

        pil_image = validated_image.image
        img_w, img_h = pil_image.size

        tile_coords = self._generate_tile_coords(img_w, img_h, slice_width, slice_height, overlap_ratio)
        full_coord = (0, 0, img_w, img_h)
        if full_coord not in tile_coords:
            tile_coords.append(full_coord)

        started_at = perf_counter()
        raw_detections: list[dict] = []

        for (x1, y1, x2, y2) in tile_coords:
            tile = pil_image.crop((x1, y1, x2, y2))
            try:
                results = model.predict(
                    source=tile,
                    conf=self._confidence_threshold,
                    iou=self._iou_threshold,
                    imgsz=self._image_size,
                    device=self._device,
                    max_det=self._max_detections,
                    verbose=False,
                )
            except Exception as exc:
                raise InferenceError(f"{self._model_name} inference failed on tile ({x1},{y1}): {exc}") from exc

            for result in results or []:
                names = self._extract_names(result)
                boxes = getattr(result, "boxes", None)
                if boxes is None:
                    continue
                for box in boxes:
                    coords = self._as_list(self._first(getattr(box, "xyxy", [])))
                    if len(coords) != 4:
                        continue
                    bx1, by1, bx2, by2 = coords
                    class_id = int(self._as_scalar(getattr(box, "cls", 0)))
                    conf = float(self._as_scalar(getattr(box, "conf", 0.0)))
                    raw_detections.append({
                        "x1": bx1 + x1,
                        "y1": by1 + y1,
                        "x2": bx2 + x1,
                        "y2": by2 + y1,
                        "conf": conf,
                        "class_id": class_id,
                        "label": names.get(class_id, str(class_id)),
                    })

        filtered = self._apply_class_aware_nms(raw_detections, postprocess_iou_threshold)
        detections = [
            DetectionObject(
                class_id=d["class_id"],
                label=d["label"],
                confidence=round(d["conf"], 4),
                bbox=BoundingBox(
                    x1=round(d["x1"], 2),
                    y1=round(d["y1"], 2),
                    x2=round(d["x2"], 2),
                    y2=round(d["y2"], 2),
                    width=round(max(d["x2"] - d["x1"], 0.0), 2),
                    height=round(max(d["y2"] - d["y1"], 0.0), 2),
                ),
            )
            for d in filtered
        ]
        detections.sort(key=lambda d: d.confidence, reverse=True)
        class_counts = dict(Counter(d.label for d in detections))

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
                confidence_threshold=self._confidence_threshold,
                iou_threshold=self._iou_threshold,
                inference_ms=round((perf_counter() - started_at) * 1000, 2),
            ),
        )

    @staticmethod
    def _generate_tile_coords(
        img_w: int,
        img_h: int,
        slice_w: int,
        slice_h: int,
        overlap_ratio: float,
    ) -> list[tuple[int, int, int, int]]:
        stride_x = max(1, int(slice_w * (1 - overlap_ratio)))
        stride_y = max(1, int(slice_h * (1 - overlap_ratio)))
        coords: list[tuple[int, int, int, int]] = []
        y = 0
        while True:
            x = 0
            while True:
                x2 = min(x + slice_w, img_w)
                y2 = min(y + slice_h, img_h)
                coords.append((x, y, x2, y2))
                if x2 >= img_w:
                    break
                x += stride_x
            if y2 >= img_h:
                break
            y += stride_y
        return coords

    @classmethod
    def _apply_class_aware_nms(
        cls,
        detections: list[dict],
        iou_threshold: float,
    ) -> list[dict]:
        if not detections:
            return []
        by_class: dict[int, list[dict]] = {}
        for det in detections:
            by_class.setdefault(det["class_id"], []).append(det)
        result: list[dict] = []
        for class_dets in by_class.values():
            sorted_dets = sorted(class_dets, key=lambda d: d["conf"], reverse=True)
            suppressed = [False] * len(sorted_dets)
            for i, det_i in enumerate(sorted_dets):
                if suppressed[i]:
                    continue
                result.append(det_i)
                for j in range(i + 1, len(sorted_dets)):
                    if not suppressed[j] and cls._compute_iou(det_i, sorted_dets[j]) > iou_threshold:
                        suppressed[j] = True
        return result

    @staticmethod
    def _compute_iou(a: dict, b: dict) -> float:
        ix1 = max(a["x1"], b["x1"])
        iy1 = max(a["y1"], b["y1"])
        ix2 = min(a["x2"], b["x2"])
        iy2 = min(a["y2"], b["y2"])
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        area_a = max(0.0, a["x2"] - a["x1"]) * max(0.0, a["y2"] - a["y1"])
        area_b = max(0.0, b["x2"] - b["x1"]) * max(0.0, b["y2"] - b["y1"])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is not None:
                return self._model

            weights_path = self._weights_path
            if not weights_path.exists():
                raise ModelNotConfiguredError(
                    f"{self._model_name} weights were not found at "
                    f"'{weights_path}'. Configure the matching WASTE_*_WEIGHTS_PATH first."
                )

            factory = self._model_factory or self._default_model_factory
            try:
                self._model = factory(str(weights_path))
            except Exception as exc:
                raise ModelNotConfiguredError(
                    f"Failed to load {self._model_name} weights from "
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

    @property
    def _model_name(self) -> str:
        return self._settings.yolov26_model_name

    @property
    def _weights_path(self):
        return self._settings.resolved_weights_path

    @property
    def _confidence_threshold(self) -> float:
        return self._settings.yolov26_confidence_threshold

    @property
    def _iou_threshold(self) -> float:
        return self._settings.yolov26_iou_threshold

    @property
    def _image_size(self) -> int:
        return self._settings.yolov26_image_size

    @property
    def _max_detections(self) -> int:
        return self._settings.yolov26_max_detections

    @property
    def _device(self) -> str:
        return self._settings.yolov26_device

    @property
    def _preload_on_startup(self) -> bool:
        return self._settings.yolov26_preload_on_startup

    @property
    def _augment(self) -> bool:
        return False

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
                    raise InferenceError(f"{self._model_name} returned an invalid bounding box.")

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

        while isinstance(current, (list, tuple)) and len(current) == 1:
            nested = current[0]
            if hasattr(nested, "tolist"):
                nested = nested.tolist()
            if isinstance(nested, (list, tuple)):
                current = nested
                continue
            break

        if isinstance(current, (list, tuple)):
            try:
                return [float(item) for item in current]
            except (TypeError, ValueError) as exc:
                raise InferenceError(
                    f"{cls.__name__} returned a non-serializable bounding box."
                ) from exc

        raise InferenceError(f"{cls.__name__} returned a non-serializable bounding box.")
