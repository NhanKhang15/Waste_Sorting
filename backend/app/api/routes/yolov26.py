from fastapi import APIRouter, Depends, File, Form, UploadFile

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
    use_slicing: bool = Form(False),
    slice_width: int = Form(640),
    slice_height: int = Form(640),
    overlap_ratio: float = Form(0.2),
    postprocess_iou_threshold: float = Form(0.5),
    detector: YoloV26Detector = Depends(get_detector),
) -> DetectionResponse:
    image_bytes = await file.read()
    try:
        return detector.detect(
            filename=file.filename,
            content_type=file.content_type,
            image_bytes=image_bytes,
            use_slicing=use_slicing,
            slice_width=slice_width,
            slice_height=slice_height,
            overlap_ratio=overlap_ratio,
            postprocess_iou_threshold=postprocess_iou_threshold,
        )
    finally:
        await file.close()
