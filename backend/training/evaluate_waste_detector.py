from __future__ import annotations

import argparse
import json
from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a trained waste detector on val or test split and save a JSON report."
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=ROOT_DIR / "runs" / "waste_detector" / "waste_yolo26s_taco" / "weights" / "best.pt",
    )
    parser.add_argument("--data", type=Path, default=ROOT_DIR / "training" / "waste_dataset.yaml")
    parser.add_argument("--split", choices=("val", "test"), default="val")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT_DIR / "runs" / "waste_detector" / "eval_report.json",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=ROOT_DIR / "training" / "taco_waste_summary.json",
        help="Dataset summary JSON from build_taco_project_dataset.py for imbalance stats.",
    )
    return parser.parse_args()


def _inverse_freq_weights(box_counts: dict[str, int]) -> dict[str, float]:
    total = sum(box_counts.values())
    n = len(box_counts)
    return {
        cls: round((total / (n * count)), 4) if count > 0 else float("inf")
        for cls, count in box_counts.items()
    }


def main() -> None:
    args = parse_args()

    if not args.weights.exists():
        raise SystemExit(
            f"Weights not found: {args.weights}\n"
            "Run train_waste_detector.py first to produce best.pt."
        )
    if not args.data.exists():
        raise SystemExit(
            f"Dataset YAML not found: {args.data}\n"
            "Run build_taco_project_dataset.py first."
        )

    box_counts: dict[str, int] = {}
    image_counts: dict[str, int] = {}
    if args.summary.exists():
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        box_counts = summary.get("target_box_counts", {})
        image_counts = summary.get("target_image_counts", {})

    model = YOLO(str(args.weights))
    metrics = model.val(
        data=str(args.data),
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
    )

    names: dict[int, str] = model.names
    class_names = [names[i] for i in sorted(names)]

    per_class: dict[str, dict] = {}
    for i, cls_name in enumerate(class_names):
        per_class[cls_name] = {
            "precision": round(float(metrics.box.p[i]), 4) if i < len(metrics.box.p) else None,
            "recall": round(float(metrics.box.r[i]), 4) if i < len(metrics.box.r) else None,
            "ap50": round(float(metrics.box.ap50[i]), 4) if i < len(metrics.box.ap50) else None,
            "ap50_95": round(float(metrics.box.maps[i]), 4) if i < len(metrics.box.maps) else None,
            "train_boxes": box_counts.get(cls_name),
            "train_images": image_counts.get(cls_name),
        }

    overall = {
        "map50": round(float(metrics.box.map50), 4),
        "map50_95": round(float(metrics.box.map), 4),
        "mean_precision": round(float(metrics.box.mp), 4),
        "mean_recall": round(float(metrics.box.mr), 4),
    }

    class_weights: dict[str, float] = {}
    imbalance_ratio: float | None = None
    if box_counts:
        class_weights = _inverse_freq_weights(box_counts)
        max_count = max(box_counts.values())
        min_count = max(min(box_counts.values()), 1)
        imbalance_ratio = round(max_count / min_count, 1)

    recommendations: list[str] = []
    for cls_name, stats in per_class.items():
        if stats["recall"] is not None and stats["recall"] < 0.30:
            recommendations.append(
                f"'{cls_name}' recall={stats['recall']:.2f} (<0.30): oversample this class or add copy-paste augmentation."
            )
        if stats["train_boxes"] is not None and stats["train_boxes"] < 100:
            recommendations.append(
                f"'{cls_name}' has only {stats['train_boxes']} training boxes — "
                "re-run build_taco_project_dataset.py with --oversample."
            )
        if stats["ap50"] is not None and stats["ap50"] < 0.40:
            recommendations.append(
                f"'{cls_name}' AP50={stats['ap50']:.2f} (<0.40): primary engine will frequently fall back "
                "to COCO for queries targeting this group."
            )

    if imbalance_ratio and imbalance_ratio > 20:
        most_common = max(box_counts, key=lambda k: box_counts[k])
        least_common = min(box_counts, key=lambda k: box_counts[k])
        recommendations.append(
            f"Dataset imbalance {imbalance_ratio:.0f}x "
            f"({most_common}: {box_counts[most_common]} boxes vs {least_common}: {box_counts[least_common]}). "
            "Run build_taco_project_dataset.py --oversample --oversample-factor 15 then retrain."
        )

    report = {
        "split": args.split,
        "weights": str(args.weights),
        "overall": overall,
        "per_class": per_class,
        "class_weights_inverse_freq": class_weights,
        "dataset_imbalance_ratio": imbalance_ratio,
        "recommendations": recommendations,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== Waste Detector Evaluation ({args.split} split) ===")
    print(f"  mAP50     : {overall['map50']:.4f}")
    print(f"  mAP50-95  : {overall['map50_95']:.4f}")
    print(f"  Precision : {overall['mean_precision']:.4f}")
    print(f"  Recall    : {overall['mean_recall']:.4f}")
    print()
    print("Per-class metrics:")
    header = f"  {'Class':<14}  {'P':>6}  {'R':>6}  {'AP50':>6}  {'AP50-95':>8}  {'Boxes':>6}  {'Images':>7}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for cls_name, stats in per_class.items():
        p = f"{stats['precision']:.4f}" if stats["precision"] is not None else "  N/A "
        r = f"{stats['recall']:.4f}" if stats["recall"] is not None else "  N/A "
        ap50 = f"{stats['ap50']:.4f}" if stats["ap50"] is not None else "  N/A "
        ap5095 = f"{stats['ap50_95']:.4f}" if stats["ap50_95"] is not None else "    N/A "
        boxes = str(stats["train_boxes"]) if stats["train_boxes"] is not None else "?"
        imgs = str(stats["train_images"]) if stats["train_images"] is not None else "?"
        print(f"  {cls_name:<14}  {p:>6}  {r:>6}  {ap50:>6}  {ap5095:>8}  {boxes:>6}  {imgs:>7}")
    print()
    if recommendations:
        print("Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
        print()
    print(f"Full report saved to: {args.output}")


if __name__ == "__main__":
    main()
