# Backend

The backend is a FastAPI application that validates uploaded images, runs object detection, parses the waste DSL, and returns a structured response for the frontend.

## Main capabilities

- `GET /api/v1/healthz`
- `GET /api/v1/yolov26/model`
- `POST /api/v1/yolov26/detect`
- `GET /api/v1/waste/queries`
- `GET /api/v1/waste/models`
- `POST /api/v1/waste/find`

`/api/v1/waste/find` returns:

- normalized DSL query
- token stream
- semantic parse tree
- formal ANTLR parse tree
- matched detections
- engine selection metadata

## Environment setup

Use Python 3.11 or 3.12.
Python 3.14 is not recommended for this ML stack.
Install Git LFS before you try to run inference, because the shared weights are tracked through LFS.

```powershell
git lfs install
git lfs pull

cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`py -3.11 -m venv venv` also works if Python `3.11` is available.

Important environment variables in `.env`:

- `WASTE_YOLOV26_WEIGHTS_PATH`
- `WASTE_DETECTOR_WEIGHTS_PATH`
- `WASTE_CORS_ORIGINS`
- `WASTE_HYBRID_WEAK_GROUPS`
- `WASTE_HYBRID_GROUP_MIN_CONFIDENCE`
- `WASTE_HYBRID_STRATEGY`
- `WASTE_DETECTOR_USE_TTA`

The checked-in `.env.example` is aligned with the current shared demo configuration:

- `WASTE_HYBRID_STRATEGY=merge`
- `WASTE_HYBRID_WEAK_GROUPS=organic`
- `WASTE_HYBRID_GROUP_MIN_CONFIDENCE=recyclable=0.40,inorganic=0.22`
- both detector devices default to `cpu` for portability

If you have CUDA configured, you can change:

- `WASTE_YOLOV26_DEVICE=0`
- `WASTE_DETECTOR_DEVICE=0`

Tracked weight files expected after `git lfs pull`:

- `runtime/weights/yolo26n.pt`
- `runs/waste_detector/waste_yolo26s_taco/weights/best.pt`

## Run the API

```powershell
python main.py
```

Or with uvicorn:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Tests

```powershell
pytest tests -q
```

The backend test suite covers configuration parsing, API routes, DSL parsing, rule matching, hybrid engine selection, image validation, and detector serialization.

## Notes

- Live inference requires model weights to exist at the configured paths.
- If you cloned before installing Git LFS, run `git lfs pull` once before starting the backend.
- The custom detector extends the shared YOLO detector implementation.
- The DSL grammar lives in `antlr/grammar/WasteQuery.g4`.
- Regenerate parser artifacts with `antlr/generate_parser.ps1` after grammar changes.
