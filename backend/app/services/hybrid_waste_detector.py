from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.core.config import Settings
from app.core.errors import InferenceError, ModelNotConfiguredError
from app.schemas.waste import (
    HybridWasteModelsResponse,
    WasteEngineResult,
    WasteFindResponse,
)
from app.schemas.yolov26 import DetectionObject, DetectionSummary
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
            primary_min_confidence=self._settings.hybrid_primary_min_confidence,
            primary_min_matches=self._settings.hybrid_primary_min_matches,
        )

    def find(
        self,
        *,
        query: str,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
        use_slicing: bool = False,
        slice_width: int = 640,
        slice_height: int = 640,
        overlap_ratio: float = 0.2,
    ) -> WasteFindResponse:
        parsed_query = self._matcher.parse_query(query)
        sahi_kwargs: dict = dict(
            use_slicing=use_slicing,
            slice_width=slice_width,
            slice_height=slice_height,
            overlap_ratio=overlap_ratio,
        )

        if self._settings.hybrid_strategy == "merge":
            return self._find_merged(
                parsed_query=parsed_query,
                filename=filename,
                content_type=content_type,
                image_bytes=image_bytes,
                **sahi_kwargs,
            )

        primary_execution = self._run_engine(
            engine=PRIMARY_ENGINE,
            detector=self._primary_detector,
            parsed_query=parsed_query,
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
            **sahi_kwargs,
        )

        if self._should_use_primary(primary_execution.result, parsed_query.waste_group):
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
            **sahi_kwargs,
        )

        if fallback_execution.result is not None:
            return self._build_response(
                parsed_query=parsed_query,
                final_result=fallback_execution.result,
                decision_reason=self._build_fallback_reason(primary_execution, parsed_query.waste_group),
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
        use_slicing: bool = False,
        slice_width: int = 640,
        slice_height: int = 640,
        overlap_ratio: float = 0.2,
    ) -> EngineExecution:
        try:
            response = detector.detect(
                filename=filename,
                content_type=content_type,
                image_bytes=image_bytes,
                use_slicing=use_slicing,
                slice_width=slice_width,
                slice_height=slice_height,
                overlap_ratio=overlap_ratio,
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

    def _should_use_primary(self, result: WasteEngineResult | None, waste_group: str) -> bool:
        if result is None:
            return False
        # Skip primary entirely for groups with insufficient training coverage.
        if waste_group.lower() in self._settings.weak_group_list:
            return False
        if result.match_count < self._settings.hybrid_primary_min_matches:
            return False
        if result.max_match_confidence is None:
            return False
        # Use per-group override if configured, otherwise fall back to global threshold.
        overrides = self._settings.group_confidence_overrides
        min_conf = overrides.get(waste_group.lower(), self._settings.hybrid_primary_min_confidence)
        return result.max_match_confidence >= min_conf

    def _find_merged(
        self,
        *,
        parsed_query: ParsedWasteQuery,
        filename: str | None,
        content_type: str | None,
        image_bytes: bytes,
        **sahi_kwargs,
    ) -> WasteFindResponse:
        """Run both engines simultaneously and merge results via spatial NMS.

        Unlike the fallback strategy, merge mode always runs both engines and
        keeps the union of their detections after suppressing spatial duplicates.
        This gives the best of both worlds: domain-specific primary labels are
        preferred when they overlap with COCO detections; otherwise, both sets
        of detections contribute independently.
        """
        primary_execution = self._run_engine(
            engine=PRIMARY_ENGINE,
            detector=self._primary_detector,
            parsed_query=parsed_query,
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
            **sahi_kwargs,
        )
        fallback_execution = self._run_engine(
            engine=FALLBACK_ENGINE,
            detector=self._fallback_detector,
            parsed_query=parsed_query,
            filename=filename,
            content_type=content_type,
            image_bytes=image_bytes,
            **sahi_kwargs,
        )

        if primary_execution.result is None and fallback_execution.result is None:
            for exc in (fallback_execution.error, primary_execution.error):
                if exc is not None:
                    raise exc
            raise InferenceError("Merge strategy: both engines failed to produce results.")

        if fallback_execution.result is None:
            return self._build_response(
                parsed_query=parsed_query,
                final_result=primary_execution.result,  # type: ignore[arg-type]
                decision_reason="Merge mode: COCO fallback unavailable; using primary detector only.",
                primary_result=primary_execution.result,
                fallback_result=None,
                primary_error=None,
                fallback_error=self._stringify_error(fallback_execution.error),
            )

        if primary_execution.result is None:
            return self._build_response(
                parsed_query=parsed_query,
                final_result=fallback_execution.result,
                decision_reason="Merge mode: primary detector unavailable; using COCO fallback only.",
                primary_result=None,
                fallback_result=fallback_execution.result,
                primary_error=self._stringify_error(primary_execution.error),
                fallback_error=None,
            )

        primary_result = primary_execution.result
        fallback_result = fallback_execution.result

        merged_matches = self._spatial_nms_merge(primary_result.matches, fallback_result.matches)
        max_conf = max((m.confidence for m in merged_matches), default=None)

        class_counts = dict(Counter(d.label for d in merged_matches))
        merged_summary = DetectionSummary(
            total_detections=len(merged_matches),
            unique_labels=sorted(class_counts),
            class_counts=class_counts,
            confidence_threshold=min(
                primary_result.summary.confidence_threshold,
                fallback_result.summary.confidence_threshold,
            ),
            iou_threshold=0.5,
            inference_ms=round(
                primary_result.summary.inference_ms + fallback_result.summary.inference_ms, 2
            ),
        )
        merged_result = WasteEngineResult(
            engine="merged",
            model=fallback_result.model,
            image=fallback_result.image,
            detections=fallback_result.detections,
            summary=merged_summary,
            matches=merged_matches,
            match_count=len(merged_matches),
            max_match_confidence=max_conf,
        )

        p_n = primary_result.match_count
        p_conf = f"{primary_result.max_match_confidence:.2f}" if primary_result.max_match_confidence is not None else "N/A"
        f_n = fallback_result.match_count
        f_conf = f"{fallback_result.max_match_confidence:.2f}" if fallback_result.max_match_confidence is not None else "N/A"
        decision_reason = (
            f"Merge strategy: primary found {p_n} match(es) (max_conf={p_conf}), "
            f"fallback found {f_n} match(es) (max_conf={f_conf}). "
            f"Spatial NMS merge yielded {len(merged_matches)} detection(s)."
        )
        return self._build_response(
            parsed_query=parsed_query,
            final_result=merged_result,
            decision_reason=decision_reason,
            primary_result=primary_result,
            fallback_result=fallback_result,
            primary_error=None,
            fallback_error=None,
        )

    @staticmethod
    def _detection_iou(a: DetectionObject, b: DetectionObject) -> float:
        ix1 = max(a.bbox.x1, b.bbox.x1)
        iy1 = max(a.bbox.y1, b.bbox.y1)
        ix2 = min(a.bbox.x2, b.bbox.x2)
        iy2 = min(a.bbox.y2, b.bbox.y2)
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        area_a = a.bbox.width * a.bbox.height
        area_b = b.bbox.width * b.bbox.height
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    @classmethod
    def _spatial_nms_merge(
        cls,
        primary_matches: list[DetectionObject],
        fallback_matches: list[DetectionObject],
        iou_threshold: float = 0.5,
    ) -> list[DetectionObject]:
        """Merge two detection lists via greedy spatial NMS (label-agnostic).

        Higher-confidence detections are kept; lower-confidence ones that
        overlap the same region (IoU > iou_threshold) are suppressed.
        Primary detections are sorted before fallback ones of equal confidence
        so that domain-specific labels are preferred on ties.
        """
        all_dets = sorted(
            primary_matches + fallback_matches,
            key=lambda d: (d.confidence, d in primary_matches),
            reverse=True,
        )
        suppressed = [False] * len(all_dets)
        kept: list[DetectionObject] = []
        for i, det_i in enumerate(all_dets):
            if suppressed[i]:
                continue
            kept.append(det_i)
            for j in range(i + 1, len(all_dets)):
                if not suppressed[j] and cls._detection_iou(det_i, all_dets[j]) > iou_threshold:
                    suppressed[j] = True
        return kept

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

    def _build_fallback_reason(self, primary_execution: EngineExecution, waste_group: str = "") -> str:
        if waste_group and waste_group.lower() in self._settings.weak_group_list:
            return (
                f"Group '{waste_group}' is listed in WASTE_HYBRID_WEAK_GROUPS because the primary model "
                "has insufficient training coverage for it. Falling back directly to COCO rule mapping."
            )

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
