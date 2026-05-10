from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.core.errors import InferenceError, ModelNotConfiguredError
from app.schemas.waste import (
    HybridWasteModelsResponse,
    WasteEngineResult,
    WasteFindResponse,
)
from app.services.waste_model_detector import WasteModelDetector
from app.services.waste_rules import ParsedWasteQuery, WasteRuleMatcher
from app.services.yolov26_detector import YoloV26Detector

PRIMARY_ENGINE = "custom_waste_detector"
FALLBACK_ENGINE = "coco_rule_map"


@dataclass(slots=True)
class EngineExecution:
    result: WasteEngineResult | None
    error: Exception | None


class HybridWasteDetector:
    def __init__(
        self,
        *,
        settings: Settings,
        primary_detector: WasteModelDetector,
        fallback_detector: YoloV26Detector,
        matcher: WasteRuleMatcher,
    ) -> None:
        self._settings = settings
        self._primary_detector = primary_detector
        self._fallback_detector = fallback_detector
        self._matcher = matcher

    def get_models_status(self) -> HybridWasteModelsResponse:
        return HybridWasteModelsResponse(
            primary_engine=PRIMARY_ENGINE,
            fallback_engine=FALLBACK_ENGINE,
            primary_model=self._primary_detector.get_model_status(),
            fallback_model=self._fallback_detector.get_model_status(),
            primary_min_confidence=self._settings.waste_hybrid_primary_min_confidence,
            primary_min_matches=self._settings.waste_hybrid_primary_min_matches,
        )

    def find(
        self,
        *,
        query: str,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
    ) -> WasteFindResponse:
        parsed_query = self._matcher.parse_query(query)

        primary_execution = self._run_engine(
            engine=PRIMARY_ENGINE,
            detector=self._primary_detector,
            parsed_query=parsed_query,
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
        )

        if self._should_use_primary(primary_execution.result):
            final_result = primary_execution.result
            assert final_result is not None
            return self._build_response(
                parsed_query=parsed_query,
                final_result=final_result,
                decision_reason=(
                    "Primary waste detector matched the requested group with sufficient confidence."
                ),
                primary_result=primary_execution.result,
                fallback_result=None,
                primary_error=None,
                fallback_error=None,
            )

        fallback_execution = self._run_engine(
            engine=FALLBACK_ENGINE,
            detector=self._fallback_detector,
            parsed_query=parsed_query,
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
        )

        if fallback_execution.result is not None:
            return self._build_response(
                parsed_query=parsed_query,
                final_result=fallback_execution.result,
                decision_reason=self._build_fallback_reason(primary_execution),
                primary_result=primary_execution.result,
                fallback_result=fallback_execution.result,
                primary_error=self._stringify_error(primary_execution.error),
                fallback_error=None,
            )

        if primary_execution.result is not None:
            return self._build_response(
                parsed_query=parsed_query,
                final_result=primary_execution.result,
                decision_reason=(
                    "Fallback detector was unavailable, so the response uses the primary detector result."
                ),
                primary_result=primary_execution.result,
                fallback_result=None,
                primary_error=None,
                fallback_error=self._stringify_error(fallback_execution.error),
            )

        for error in (fallback_execution.error, primary_execution.error):
            if error is not None:
                raise error

        raise InferenceError("Hybrid waste detection could not produce any result.")

    def _run_engine(
        self,
        *,
        engine: str,
        detector: YoloV26Detector,
        parsed_query: ParsedWasteQuery,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
    ) -> EngineExecution:
        try:
            response = detector.detect(
                filename=filename,
                content_type=content_type,
                image_bytes=image_bytes,
            )
        except (InferenceError, ModelNotConfiguredError) as exc:
            return EngineExecution(result=None, error=exc)

        matches = self._matcher.match_parsed_query(
            parsed_query=parsed_query,
            response=response,
        )
        return EngineExecution(
            result=self._build_engine_result(
                engine=engine,
                detections=response.detections,
                image=response.image,
                model=response.model,
                summary=response.summary,
                matches=matches,
            ),
            error=None,
        )

    @staticmethod
    def _build_engine_result(
        *,
        engine: str,
        detections,
        image,
        model,
        summary,
        matches,
    ) -> WasteEngineResult:
        max_match_confidence = None
        if matches:
            max_match_confidence = max(match.confidence for match in matches)

        return WasteEngineResult(
            engine=engine,
            model=model,
            image=image,
            detections=detections,
            summary=summary,
            matches=matches,
            match_count=len(matches),
            max_match_confidence=max_match_confidence,
        )

    def _should_use_primary(self, result: WasteEngineResult | None) -> bool:
        if result is None:
            return False
        if result.match_count < self._settings.waste_hybrid_primary_min_matches:
            return False
        if result.max_match_confidence is None:
            return False
        return result.max_match_confidence >= self._settings.waste_hybrid_primary_min_confidence

    @staticmethod
    def _build_response(
        *,
        parsed_query: ParsedWasteQuery,
        final_result: WasteEngineResult,
        decision_reason: str,
        primary_result: WasteEngineResult | None,
        fallback_result: WasteEngineResult | None,
        primary_error: str | None,
        fallback_error: str | None,
    ) -> WasteFindResponse:
        return WasteFindResponse(
            model=final_result.model,
            image=final_result.image,
            detections=final_result.detections,
            summary=final_result.summary,
            raw_query=parsed_query.raw_query,
            normalized_query=parsed_query.normalized_query,
            query_action=parsed_query.query_action,
            waste_group=parsed_query.waste_group,
            targets=list(parsed_query.allowed_keywords),
            tokens=[t.to_dict() for t in parsed_query.tokens],
            parse_tree=parsed_query.parse_tree,
            formal_parse_tree=parsed_query.formal_parse_tree,
            confidence_operator=parsed_query.confidence_operator,
            minimum_confidence=parsed_query.minimum_confidence,
            label_filter=parsed_query.label_filter,
            matches=final_result.matches,
            match_count=final_result.match_count,
            engine_used=final_result.engine,
            decision_reason=decision_reason,
            primary_result=primary_result,
            fallback_result=fallback_result,
            primary_error=primary_error,
            fallback_error=fallback_error,
        )

    @staticmethod
    def _stringify_error(error: Exception | None) -> str | None:
        if error is None:
            return None
        return str(error)

    def _build_fallback_reason(self, primary_execution: EngineExecution) -> str:
        if primary_execution.error is not None:
            return (
                "Primary waste detector was unavailable, so the request fell back to COCO detections plus rule mapping."
            )

        assert primary_execution.result is not None
        if primary_execution.result.match_count == 0:
            return (
                "Primary waste detector found no match for the requested group, so the request fell back to COCO detections plus rule mapping."
            )

        return (
            "Primary waste detector matched the group below the confidence threshold, so the request fell back to COCO detections plus rule mapping."
        )
