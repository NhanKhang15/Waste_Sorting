from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_detector
from app.schemas.yolov26 import DetectionResponse, ModelStatusResponse
from app.services.yolov26_detector import YoloV26Detector

router = APIRouter(prefix="/yolov26", tags=["yolov26"])


@router.get("/model", response_model=ModelStatusResponse)
def read_model_status(
    detector: YoloV26Detector = Depends(get_detector),
) -> ModelStatusResponse:
    return detector.get_model_status()


@router.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    file: UploadFile = File(...),
    detector: YoloV26Detector = Depends(get_detector),
) -> DetectionResponse:
    image_bytes = await file.read()
    try:
        return detector.detect(
            filename=file.filename,
            content_type=file.content_type,
            image_bytes=image_bytes,
        )
    finally:
        await file.close()
