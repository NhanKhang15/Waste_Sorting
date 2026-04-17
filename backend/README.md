# YOLOv26 Backend

This backend is intentionally focused on YOLOv26 inference only.
ANTLR, DSL parsing, auth, history, and frontend integration are deferred.

## Scope

- FastAPI service dedicated to YOLOv26 detection
- Lazy model loading with configurable local weights
- Image validation before inference
- Structured JSON output for detections and model status
- Tests for config, validation, and detector serialization

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
4. Place your YOLOv26 weights at `backend/runtime/weights/yolo26n.pt`, or point `WASTE_YOLOV26_WEIGHTS_PATH` to a different local `.pt` file.

## Run

From the `backend/` directory:

```powershell
uvicorn main:app --reload
```

Swagger UI will be available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /api/v1/healthz`
- `GET /api/v1/yolov26/model`
- `POST /api/v1/yolov26/detect`

Example request:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/yolov26/detect" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@sample.png"
```

## Important Assumption

The code uses the `ultralytics` runtime to serve a YOLOv26-compatible `.pt` file.
The actual weights are not committed to the repo.
