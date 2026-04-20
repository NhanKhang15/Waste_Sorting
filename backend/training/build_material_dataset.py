from __future__ import annotations

import argparse
import csv
import random
import re
import shutil
import sys
from pathlib import Path

from PIL import Image


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.waste_sorter.annotator import gather_training_inventory, resolve_training_label_path  # noqa: E402
from backend.waste_sorter.materials import load_material_classes  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build YOLO material detection dataset from annotated images.")
    parser.add_argument("--images", type=Path, default=ROOT_DIR / "training_image")
    parser.add_argument("--labels", type=Path, default=ROOT_DIR / "training_labels")
    parser.add_argument("--classes", type=Path, default=ROOT_DIR / "training" / "material_classes.txt")
    parser.add_argument("--output", type=Path, default=ROOT_DIR / "datasets" / "material_detection")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Include images with an empty label file as negative samples.",
    )
    return parser.parse_args()


def safe_name(relative_path: str, index: int) -> str:
    stem = Path(relative_path).stem
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_") or "image"
    return f"{index:04d}_{stem}"


def count_label_lines(label_path: Path) -> int:
    if not label_path.exists():
        return 0
    return len([line for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()])


def write_yaml(dataset_root: Path, class_names: list[str], output_path: Path) -> None:
    lines = [
        f"path: {dataset_root.as_posix()}",
        "train: images/train",
        "val: images/val",
        "names:",
    ]
    lines.extend(f"  {index}: {class_name}" for index, class_name in enumerate(class_names))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def convert_image(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        image.convert("RGB").save(destination, format="JPEG", quality=95)


def main() -> None:
    args = parse_args()
    class_names = load_material_classes(args.classes)
    inventory = gather_training_inventory(images_root=args.images, labels_root=args.labels, classes=class_names)

    candidates = []
    for item in inventory:
        label_path = resolve_training_label_path(args.images, args.labels, item["path"])
        box_count = count_label_lines(label_path)
        if box_count > 0 or (args.allow_empty and label_path.exists()):
            candidates.append(item)

    if not candidates:
        raise SystemExit(
            "Không có ảnh nào đủ điều kiện để build dataset. "
            "Hãy mở /annotator để vẽ bbox và lưu label trước."
        )

    random.Random(args.seed).shuffle(candidates)
    val_count = int(round(len(candidates) * args.val_ratio)) if len(candidates) > 1 else 0
    if val_count == 0 and len(candidates) > 1:
        val_count = 1
    if val_count >= len(candidates):
        val_count = len(candidates) - 1

    split_map = {}
    for index, item in enumerate(candidates):
        split_map[item["path"]] = "val" if index < val_count else "train"

    if args.output.exists():
        shutil.rmtree(args.output)

    for split in ("train", "val"):
        (args.output / "images" / split).mkdir(parents=True, exist_ok=True)
        (args.output / "labels" / split).mkdir(parents=True, exist_ok=True)

    manifest_path = ROOT_DIR / "training" / "dataset_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["source_path", "split", "image_name", "label_name", "box_count"],
        )
        writer.writeheader()

        for index, item in enumerate(candidates, start=1):
            relative_path = item["path"]
            image_path = args.images / relative_path
            label_path = resolve_training_label_path(args.images, args.labels, relative_path)
            split = split_map[relative_path]
            file_stem = safe_name(relative_path, index)
            destination_image = args.output / "images" / split / f"{file_stem}.jpg"
            destination_label = args.output / "labels" / split / f"{file_stem}.txt"

            convert_image(image_path, destination_image)
            shutil.copy2(label_path, destination_label)

            writer.writerow(
                {
                    "source_path": relative_path,
                    "split": split,
                    "image_name": destination_image.name,
                    "label_name": destination_label.name,
                    "box_count": count_label_lines(label_path),
                }
            )

    yaml_path = ROOT_DIR / "training" / "material_dataset.yaml"
    write_yaml(args.output, class_names, yaml_path)

    train_count = len([item for item in candidates if split_map[item["path"]] == "train"])
    val_count = len(candidates) - train_count
    print(f"Built dataset at: {args.output}")
    print(f"Dataset YAML: {yaml_path}")
    print(f"Train images: {train_count}")
    print(f"Val images: {val_count}")


if __name__ == "__main__":
    main()
