from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings
from app.services.yolov26_detector import YoloV26Detector


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_detector() -> YoloV26Detector:
    return YoloV26Detector(settings=get_settings())
