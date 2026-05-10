from __future__ import annotations

from app.services.yolov26_detector import YoloV26Detector


class WasteModelDetector(YoloV26Detector):
    @property
    def _model_name(self) -> str:
        return self._settings.waste_detector_model_name

    @property
    def _weights_path(self):
        return self._settings.resolved_waste_detector_weights_path

    @property
    def _confidence_threshold(self) -> float:
        return self._settings.waste_detector_confidence_threshold

    @property
    def _iou_threshold(self) -> float:
        return self._settings.waste_detector_iou_threshold

    @property
    def _image_size(self) -> int:
        return self._settings.waste_detector_image_size

    @property
    def _max_detections(self) -> int:
        return self._settings.waste_detector_max_detections

    @property
    def _device(self) -> str:
        return self._settings.waste_detector_device

    @property
    def _preload_on_startup(self) -> bool:
        return self._settings.waste_detector_preload_on_startup
