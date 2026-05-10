from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings
from app.services.hybrid_waste_detector import HybridWasteDetector
from app.services.waste_model_detector import WasteModelDetector
from app.services.waste_rules import WasteRuleMatcher
from app.services.yolov26_detector import YoloV26Detector


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_detector() -> YoloV26Detector:
    return YoloV26Detector(settings=get_settings())


@lru_cache
def get_waste_detector() -> WasteModelDetector:
    return WasteModelDetector(settings=get_settings())


@lru_cache
def get_waste_rule_matcher() -> WasteRuleMatcher:
    return WasteRuleMatcher()


@lru_cache
def get_hybrid_waste_detector() -> HybridWasteDetector:
    return HybridWasteDetector(
        settings=get_settings(),
        primary_detector=get_waste_detector(),
        fallback_detector=get_detector(),
        matcher=get_waste_rule_matcher(),
    )
