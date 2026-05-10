from fastapi import APIRouter, Depends

from app.api.deps import get_detector, get_settings
from app.core.config import Settings
from app.schemas.yolov26 import HealthResponse
from app.services.yolov26_detector import YoloV26Detector

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
def read_health(
    settings: Settings = Depends(get_settings),
    detector: YoloV26Detector = Depends(get_detector),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        model=detector.get_model_status(),
    )
