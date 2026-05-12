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

    # Augmentation hyperparameters — tune these when class imbalance is high.
    aug = parser.add_argument_group("augmentation")
    aug.add_argument("--degrees", type=float, default=10.0,
                     help="Rotation augmentation range ±degrees (0=off).")
    aug.add_argument("--translate", type=float, default=0.1,
                     help="Translation augmentation fraction (0–0.9).")
    aug.add_argument("--scale", type=float, default=0.5,
                     help="Scale augmentation gain (0–0.9).")
    aug.add_argument("--fliplr", type=float, default=0.5,
                     help="Horizontal flip probability (0–1).")
    aug.add_argument("--flipud", type=float, default=0.1,
                     help="Vertical flip probability (0–1).")
    aug.add_argument("--mosaic", type=float, default=1.0,
                     help="Mosaic augmentation probability (0–1). Helps with small-object recall.")
    aug.add_argument("--mixup", type=float, default=0.1,
                     help="Mixup augmentation probability (0–1). Smooths decision boundaries.")
    aug.add_argument("--copy-paste", type=float, default=0.1,
                     help="Copy-paste augmentation probability (0–1). Pastes extra objects into scenes.")
    aug.add_argument("--close-mosaic", type=int, default=10,
                     help="Disable mosaic in the last N epochs to stabilise training.")
    aug.add_argument("--freeze", type=int, default=0,
                     help="Freeze the first N backbone layers (0 = full fine-tune).")
    aug.add_argument("--label-smoothing", type=float, default=0.0,
                     help=(
                         "Label-smoothing epsilon for BCE classification loss (0–0.1). "
                         "Reduces overconfidence on minority classes; start with 0.01–0.05."
                     ))
    aug.add_argument("--cls-pw", type=float, default=1.0,
                     help=(
                         "Positive-class weight for BCE object-classification loss. "
                         "Increase (e.g. 2.0–5.0) to penalise false negatives on minority classes."
                     ))

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
        # Augmentation
        degrees=args.degrees,
        translate=args.translate,
        scale=args.scale,
        fliplr=args.fliplr,
        flipud=args.flipud,
        mosaic=args.mosaic,
        mixup=args.mixup,
        copy_paste=args.copy_paste,
        close_mosaic=args.close_mosaic,
        freeze=args.freeze if args.freeze > 0 else None,
        label_smoothing=args.label_smoothing,
        cls_pw=args.cls_pw,
    )

    best_path = args.project / args.name / "weights" / "best.pt"
    print(f"Training completed. Best weights: {best_path}")


if __name__ == "__main__":
    main()
