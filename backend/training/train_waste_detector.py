from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO26 waste-sorting detector on the remapped TACO dataset.")
    parser.add_argument("--model", default="yolo26s.pt", help="Base YOLO26 model to fine-tune.")
    parser.add_argument("--data", type=Path, default=ROOT_DIR / "training" / "waste_dataset.yaml")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--project", type=Path, default=ROOT_DIR / "runs" / "waste_detector")
    parser.add_argument("--name", default="waste_yolo26s_taco")
    parser.add_argument("--device", default=None)
    parser.add_argument("--patience", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.data.exists():
        raise SystemExit(
            "Không tìm thấy training/waste_dataset.yaml. "
            "Hãy chạy training/build_taco_project_dataset.py trước."
        )

    model = YOLO(args.model)
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(args.project),
        name=args.name,
        device=args.device,
        patience=args.patience,
        pretrained=True,
        exist_ok=True,
    )

    best_path = args.project / args.name / "weights" / "best.pt"
    print(f"Training completed. Best weights: {best_path}")


if __name__ == "__main__":
    main()
