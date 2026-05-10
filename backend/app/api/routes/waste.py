from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_hybrid_waste_detector, get_waste_rule_matcher
from app.schemas.waste import (
    HybridWasteModelsResponse,
    SupportedWasteQueriesResponse,
    WasteFindResponse,
)
from app.services.hybrid_waste_detector import HybridWasteDetector
from app.services.waste_rules import WasteRuleMatcher

router = APIRouter(prefix="/waste", tags=["waste"])


@router.get("/queries", response_model=SupportedWasteQueriesResponse)
def read_supported_queries(
    matcher: WasteRuleMatcher = Depends(get_waste_rule_matcher),
) -> SupportedWasteQueriesResponse:
    return SupportedWasteQueriesResponse(
        supported_groups=matcher.supported_groups(),
        supported_queries=matcher.supported_queries(),
        group_keywords=matcher.group_keywords(),
        dsl_examples=matcher.supported_dsl_examples(),
    )


@router.get("/models", response_model=HybridWasteModelsResponse)
def read_waste_models(
    hybrid_detector: HybridWasteDetector = Depends(get_hybrid_waste_detector),
) -> HybridWasteModelsResponse:
    return hybrid_detector.get_models_status()


@router.post("/find", response_model=WasteFindResponse)
async def find_waste_matches(
    query: str = Form(...),
    file: UploadFile = File(...),
    hybrid_detector: HybridWasteDetector = Depends(get_hybrid_waste_detector),
) -> WasteFindResponse:
    image_bytes = await file.read()
    try:
        return hybrid_detector.find(
            query=query,
            filename=file.filename,
            content_type=file.content_type,
            image_bytes=image_bytes,
        )
    finally:
        await file.close()
