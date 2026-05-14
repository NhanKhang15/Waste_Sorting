# Waste Sorting

Waste Sorting is a monorepo for image-based waste classification with a FastAPI backend and a React frontend.
The backend combines a custom waste detector, a COCO fallback detector, and an ANTLR-powered DSL.
The frontend lets you upload an image, submit a waste query, and inspect tokens, parse trees, and engine decisions.

## Highlights

- FastAPI REST API for health, model status, raw COCO detection, and hybrid waste detection
- Hybrid detection pipeline with primary custom model, COCO fallback, and optional merge strategy
- ANTLR DSL with token stream, semantic AST, and formal parse tree responses
- React dashboard with image overlays, DSL viewer, token chips, parse tree visualization, and engine diagnostics
- Optional SAHI slicing toggle for dense or high-resolution images

## Repository layout

```text
Waste_Sorting/
|- backend/
|  |- app/
|  |- antlr/
|  |- dsl/
|  |- tests/
|  `- training/
|- frontend/
`- PROJECT_PROGRESS.md
```

## Prerequisites

- Python 3.11 or 3.12
- Node.js 18 or newer
- Git LFS
- Model weights available at the paths configured in `backend/.env`

Python 3.14 is not recommended for this project because common ML dependencies in this stack are not compatible with it yet.

## Model Weights

The shared inference weights are versioned with Git LFS:

- `backend/runtime/weights/yolo26n.pt`
- `backend/runs/waste_detector/waste_yolo26s_taco/weights/best.pt`

Install Git LFS before cloning, or run `git lfs pull` after cloning:

```powershell
git lfs install
git lfs pull
```

If those files are missing, the backend can start but live inference endpoints will fail when they try to load the models.

## Quick start

### Backend

```powershell
git lfs install
git lfs pull

cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

Notes:

- `py -3.11 -m venv venv` also works if Python `3.11` is installed.
- `backend/.env.example` is tuned for the current hybrid demo setup and uses `cpu` by default for portability.
- If you have CUDA configured, you can switch `WASTE_YOLOV26_DEVICE` and `WASTE_DETECTOR_DEVICE` from `cpu` to `0`.

Backend API docs will be available at `http://127.0.0.1:8000/docs`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm.cmd run dev
```

If PowerShell blocks `npm.ps1`, use `npm.cmd` for all npm commands.

Frontend will be available at `http://localhost:5173`.

## Verification commands

```powershell
cd frontend
npm.cmd run build
npm.cmd run lint
```

```powershell
cd backend
pytest tests -q
```

If you cloned the repo before installing Git LFS, rerun `git lfs pull` before testing inference.

## More documentation

- Backend setup and API details: [backend/README.md](backend/README.md)
- Frontend setup and scripts: [frontend/README.md](frontend/README.md)
- Historical implementation notes: [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)
