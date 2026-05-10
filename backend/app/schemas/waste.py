from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.yolov26 import (
    DetectionObject,
    DetectionResponse,
    DetectionSummary,
    ImageMetadata,
    ModelStatusResponse,
)


class SupportedWasteQueriesResponse(BaseModel):
    supported_groups: list[str]
    supported_queries: list[str]
    group_keywords: dict[str, list[str]]
    dsl_examples: list[str]


class TokenInfoModel(BaseModel):
    type: str
    text: str


class WasteQueryTreeNode(BaseModel):
    name: str
    is_terminal: bool = False
    text: str | None = None
    children: list["WasteQueryTreeNode"] = Field(default_factory=list)


class WasteEngineResult(BaseModel):
    engine: str
    model: ModelStatusResponse
    image: ImageMetadata
    detections: list[DetectionObject]
    summary: DetectionSummary
    matches: list[DetectionObject]
    match_count: int = Field(..., ge=0)
    max_match_confidence: float | None = Field(default=None, ge=0, le=1)


class HybridWasteModelsResponse(BaseModel):
    primary_engine: str
    fallback_engine: str
    primary_model: ModelStatusResponse
    fallback_model: ModelStatusResponse
    primary_min_confidence: float = Field(..., gt=0, le=1)
    primary_min_matches: int = Field(..., ge=1)


class WasteFindResponse(DetectionResponse):
    raw_query: str
    normalized_query: str
    query_action: str
    waste_group: str
    targets: list[str]
    tokens: list[TokenInfoModel]
    parse_tree: WasteQueryTreeNode
    formal_parse_tree: WasteQueryTreeNode
    confidence_operator: str | None = None
    minimum_confidence: float | None = Field(default=None, ge=0, le=1)
    label_filter: str | None = None
    matches: list[DetectionObject]
    match_count: int = Field(..., ge=0)
    engine_used: str
    decision_reason: str
    primary_result: WasteEngineResult | None = None
    fallback_result: WasteEngineResult | None = None
    primary_error: str | None = None
    fallback_error: str | None = None


WasteQueryTreeNode.model_rebuild()
