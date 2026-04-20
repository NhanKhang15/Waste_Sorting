from __future__ import annotations

import hashlib
import os
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from PIL import Image
from werkzeug.utils import secure_filename

from backend.waste_sorter.annotator import (
    gather_training_inventory,
    load_annotations,
    resolve_training_image_path,
    resolve_training_label_path,
    save_annotations,
)
from backend.waste_sorter.detector import QueryError, WasteFinder
from backend.waste_sorter.materials import load_material_classes


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
CROP_DIR = STATIC_DIR / "crops"
ANNOTATED_DIR = STATIC_DIR / "annotated"
TRAINING_IMAGE_DIR = BASE_DIR / "training_image"
TRAINING_LABEL_DIR = BASE_DIR / "training_labels"
TRAINING_DIR = BASE_DIR / "training"
MATERIAL_CLASSES_FILE = TRAINING_DIR / "material_classes.txt"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONF", "0.25"))
IOU_THRESHOLD = float(os.getenv("YOLO_IOU", "0.45"))
IMAGE_SIZE = int(os.getenv("YOLO_IMGSZ", "640"))
MAX_DETECTIONS = int(os.getenv("YOLO_MAX_DET", "300"))
MODEL_WEIGHTS = os.getenv("YOLO_MODEL", "yolo26s.pt")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

for directory in (UPLOAD_DIR, CROP_DIR, ANNOTATED_DIR, TRAINING_LABEL_DIR, TRAINING_DIR):
    directory.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(STATIC_DIR))
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/static/*": {"origins": "*"}})

detector = WasteFinder(model_path=MODEL_WEIGHTS, confidence=CONFIDENCE_THRESHOLD)


def build_static_url(folder: str, filename: str) -> str:
    return f"/static/{folder}/{filename}"


def weights_path() -> Path:
    candidate = Path(MODEL_WEIGHTS)
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate


def model_status_payload() -> dict:
    wp = weights_path()
    loaded = detector._model is not None
    device = "cpu"
    if loaded:
        try:
            device = str(next(detector._model.model.parameters()).device)
        except Exception:  # noqa: BLE001
            device = "cpu"
    return {
        "name": Path(MODEL_WEIGHTS).stem,
        "weights_path": str(wp),
        "weights_present": wp.exists(),
        "model_loaded": loaded,
        "device": device,
        "image_size": IMAGE_SIZE,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "iou_threshold": IOU_THRESHOLD,
        "max_detections": MAX_DETECTIONS,
        "preload_on_startup": False,
    }


def run_yolo(image_path: Path) -> tuple[list[dict], float]:
    started = time.perf_counter()
    results = detector.model.predict(
        source=str(image_path),
        conf=CONFIDENCE_THRESHOLD,
        iou=IOU_THRESHOLD,
        imgsz=IMAGE_SIZE,
        max_det=MAX_DETECTIONS,
        verbose=False,
    )
    inference_ms = (time.perf_counter() - started) * 1000.0

    prediction = results[0]
    detections: list[dict] = []
    for box in prediction.boxes:
        class_id = int(box.cls.item())
        label = detector.class_names.get(class_id, str(class_id))
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
        detections.append(
            {
                "class_id": class_id,
                "label": label,
                "confidence": round(float(box.conf.item()), 4),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "width": max(0.0, x2 - x1),
                    "height": max(0.0, y2 - y1),
                },
            }
        )
    return detections, inference_ms


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/annotator")
def annotator() -> str:
    return render_template("annotator.html")


@app.get("/api/v1/healthz")
def healthz():
    return jsonify(
        {
            "status": "ok",
            "service": "waste-sorter-api",
            "version": APP_VERSION,
            "model": model_status_payload(),
        }
    )


@app.get("/api/v1/yolov26/model")
def yolov26_model():
    return jsonify(model_status_payload())


@app.post("/api/v1/yolov26/detect")
def yolov26_detect():
    image = request.files.get("file") or request.files.get("image")
    if image is None or not image.filename:
        return jsonify({"detail": "Please choose an image first."}), 400

    extension = Path(image.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"detail": "Supported image types: .jpg, .jpeg, .png, .webp."}), 400

    safe_stem = secure_filename(Path(image.filename).stem) or "upload"
    upload_name = f"{safe_stem}_{uuid.uuid4().hex[:8]}{extension}"
    upload_path = UPLOAD_DIR / upload_name

    raw_bytes = image.stream.read()
    upload_path.write_bytes(raw_bytes)

    try:
        with Image.open(upload_path) as pil_image:
            width, height = pil_image.size
            img_format = (pil_image.format or extension.lstrip(".")).upper()
    except Exception:  # noqa: BLE001
        return jsonify({"detail": "The uploaded image could not be read."}), 400

    try:
        detections, inference_ms = run_yolo(upload_path)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"detail": f"Image processing failed: {exc}"}), 500

    class_counts: dict[str, int] = {}
    for det in detections:
        class_counts[det["label"]] = class_counts.get(det["label"], 0) + 1

    payload = {
        "model": model_status_payload(),
        "image": {
            "filename": image.filename,
            "content_type": image.mimetype or "application/octet-stream",
            "size_bytes": len(raw_bytes),
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "width": width,
            "height": height,
            "format": img_format,
        },
        "detections": detections,
        "summary": {
            "total_detections": len(detections),
            "unique_labels": sorted(class_counts.keys()),
            "class_counts": class_counts,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "iou_threshold": IOU_THRESHOLD,
            "inference_ms": round(inference_ms, 2),
        },
        "uploaded_image": build_static_url("uploads", upload_path.name),
    }
    return jsonify(payload)


@app.post("/api/find")
def find_waste():
    image = request.files.get("image")
    query = request.form.get("query", "")

    if image is None or not image.filename:
        return jsonify({"error": "Please choose an image first."}), 400

    extension = Path(image.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Supported image types: .jpg, .jpeg, .png, .webp."}), 400

    safe_stem = secure_filename(Path(image.filename).stem) or "upload"
    upload_name = f"{safe_stem}_{uuid.uuid4().hex[:8]}{extension}"
    upload_path = UPLOAD_DIR / upload_name
    image.save(upload_path)

    try:
        payload = detector.find_matches(
            image_path=upload_path,
            query=query,
            crop_dir=CROP_DIR,
            annotated_dir=ANNOTATED_DIR,
        )
    except QueryError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Image processing failed: {exc}"}), 500

    payload["uploaded_image"] = build_static_url("uploads", upload_path.name)
    return jsonify(payload)


@app.get("/api/annotator/files")
def annotator_files():
    material_classes = load_material_classes(MATERIAL_CLASSES_FILE)
    inventory = gather_training_inventory(
        images_root=TRAINING_IMAGE_DIR,
        labels_root=TRAINING_LABEL_DIR,
        classes=material_classes,
    )
    return jsonify(
        {
            "classes": material_classes,
            "images": inventory,
            "image_root": str(TRAINING_IMAGE_DIR),
            "label_root": str(TRAINING_LABEL_DIR),
        }
    )


@app.get("/api/annotator/image")
def annotator_image():
    relative_path = request.args.get("path", "")
    image_path = resolve_training_image_path(TRAINING_IMAGE_DIR, relative_path)
    return send_file(image_path)


@app.get("/api/annotator/annotations")
def annotator_annotations():
    relative_path = request.args.get("image", "")
    material_classes = load_material_classes(MATERIAL_CLASSES_FILE)
    image_path = resolve_training_image_path(TRAINING_IMAGE_DIR, relative_path)
    label_path = resolve_training_label_path(TRAINING_IMAGE_DIR, TRAINING_LABEL_DIR, relative_path)
    payload = load_annotations(
        image_path=image_path,
        label_path=label_path,
        classes=material_classes,
        relative_path=relative_path,
    )
    return jsonify(payload)


@app.post("/api/annotator/save")
def annotator_save():
    payload = request.get_json(silent=True) or {}
    relative_path = payload.get("image", "")
    annotations = payload.get("annotations", [])
    material_classes = load_material_classes(MATERIAL_CLASSES_FILE)

    image_path = resolve_training_image_path(TRAINING_IMAGE_DIR, relative_path)
    label_path = resolve_training_label_path(TRAINING_IMAGE_DIR, TRAINING_LABEL_DIR, relative_path)
    saved = save_annotations(
        image_path=image_path,
        label_path=label_path,
        classes=material_classes,
        annotations=annotations,
        relative_path=relative_path,
    )
    return jsonify(saved)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(debug=True, host="0.0.0.0", port=port)
