# YOLOv26 Backend

This backend is standardized around the `FastAPI` app in `backend/app/`.
The current detection flow is hybrid: a trained waste detector runs first, then the API falls back to COCO detections plus rule mapping when needed.

## Scope

- FastAPI service dedicated to waste and YOLO inference
- Lazy model loading with configurable local weights
- Image validation before inference
- Hybrid waste matching: custom waste model first, COCO plus rule mapping as fallback
- Structured JSON output for detections, model status, and hybrid decisions
- Tests for config, validation, detector serialization, and hybrid waste routing

## Project Layout

```text
backend/
  app/
    api/
    core/
    schemas/
    services/
  runtime/
    weights/
  runs/
    waste_detector/
  tests/
  main.py
  requirements.txt
```

## Setup

1. Create a virtual environment.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` if you want custom settings.
4. Keep the COCO fallback weights at `backend/runtime/weights/yolo26n.pt`.
5. Keep the trained waste model at `backend/runs/waste_detector/waste_yolo26s_taco/weights/best.pt`, or override `WASTE_DETECTOR_WEIGHTS_PATH`.

## Run

From the `backend/` directory:

```powershell
uvicorn main:app --reload
```

Or:

```powershell
python main.py
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /api/v1/healthz`
- `GET /api/v1/yolov26/model`
- `POST /api/v1/yolov26/detect`
- `GET /api/v1/waste/queries`
- `GET /api/v1/waste/models`
- `POST /api/v1/waste/find`

Example request for hybrid waste detection:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/waste/find" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "query=find me recyclable waste" `
  -F "file=@sample.png"
```

The response includes `engine_used`, `decision_reason`, `primary_result`, and `fallback_result` so you can see which branch won.

## Supported Waste Queries

- `find me organic waste`
- `find me recyclable waste`
- `find me inorganic waste`
