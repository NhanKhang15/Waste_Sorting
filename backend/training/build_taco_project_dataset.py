from __future__ import annotations

import argparse
import csv
import json
import os
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TACO_ANNOTATIONS = ROOT_DIR / "datasets" / "taco" / "metadata" / "annotations.json"
DEFAULT_TACO_IMAGES = ROOT_DIR / "datasets" / "taco" / "images"
DEFAULT_MAPPING = ROOT_DIR / "training" / "taco_project_mapping.json"
DEFAULT_CLASSES = ROOT_DIR / "training" / "waste_classes.txt"
DEFAULT_OUTPUT = ROOT_DIR / "datasets" / "waste_sorting_taco"
DEFAULT_YAML = ROOT_DIR / "training" / "waste_dataset.yaml"
DEFAULT_MANIFEST = ROOT_DIR / "training" / "taco_waste_manifest.csv"
DEFAULT_SUMMARY = ROOT_DIR / "training" / "taco_waste_summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert TACO COCO annotations into a project-specific YOLO dataset.")
    parser.add_argument("--annotations", type=Path, default=DEFAULT_TACO_ANNOTATIONS)
    parser.add_argument("--images-root", type=Path, default=DEFAULT_TACO_IMAGES)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--yaml-output", type=Path, default=DEFAULT_YAML)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--copy-mode",
        choices=("hardlink", "copy"),
        default="hardlink",
        help="Use hardlink to save disk when source and destination are on the same drive.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Keep images without mapped boxes as background images.",
    )
    return parser.parse_args()


def load_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_mapping(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_yaml(dataset_root: Path, class_names: list[str], output_path: Path) -> None:
    lines = [
        f"path: {dataset_root.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "names:",
    ]
    lines.extend(f"  {index}: {class_name}" for index, class_name in enumerate(class_names))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def safe_stem(image_id: int, file_name: str) -> str:
    suffix = Path(file_name).suffix.lower()
    return f"taco_{image_id:06d}{suffix}"


def hardlink_or_copy(source: Path, destination: Path, mode: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    if mode == "hardlink":
        try:
            os.link(source, destination)
            return
        except OSError:
            pass
    shutil.copy2(source, destination)


def main() -> None:
    args = parse_args()
    annotations = json.loads(args.annotations.read_text(encoding="utf-8"))
    mapping_data = load_mapping(args.mapping)
    class_names = load_lines(args.classes)
    class_to_index = {class_name: index for index, class_name in enumerate(class_names)}
    category_mapping = mapping_data["category_mapping"]
    skip_target = mapping_data.get("skip_target", "__skip__")

    categories = {category["id"]: category["name"] for category in annotations["categories"]}
    images = {image["id"]: image for image in annotations["images"]}

    annotations_by_image: dict[int, list[dict]] = defaultdict(list)
    source_class_counts = Counter()
    target_class_counts = Counter()
    skipped_class_counts = Counter()

    for annotation in annotations["annotations"]:
        category_name = categories[annotation["category_id"]]
        source_class_counts[category_name] += 1
        mapped_target = category_mapping.get(category_name, skip_target)

        if mapped_target == skip_target:
            skipped_class_counts[category_name] += 1
            continue

        if mapped_target not in class_to_index:
            raise SystemExit(f"Mapped class '{mapped_target}' not found in {args.classes}")

        image_meta = images[annotation["image_id"]]
        width = float(image_meta["width"])
        height = float(image_meta["height"])
        x, y, box_width, box_height = annotation["bbox"]
        if box_width <= 0 or box_height <= 0 or width <= 0 or height <= 0:
            continue

        center_x = (x + box_width / 2.0) / width
        center_y = (y + box_height / 2.0) / height
        norm_width = box_width / width
        norm_height = box_height / height

        annotations_by_image[annotation["image_id"]].append(
            {
                "class_name": mapped_target,
                "class_id": class_to_index[mapped_target],
                "yolo": (
                    center_x,
                    center_y,
                    norm_width,
                    norm_height,
                ),
                "source_category": category_name,
            }
        )
        target_class_counts[mapped_target] += 1

    candidate_images = []
    for image_id, image_meta in images.items():
        boxes = annotations_by_image.get(image_id, [])
        if boxes or args.allow_empty:
            candidate_images.append(image_meta)

    if not candidate_images:
        raise SystemExit("No TACO images left after applying the current mapping.")

    random.Random(args.seed).shuffle(candidate_images)
    total_images = len(candidate_images)
    val_count = int(round(total_images * args.val_ratio))
    test_count = int(round(total_images * args.test_ratio))
    if total_images >= 3:
        val_count = max(1, val_count)
        test_count = max(1, test_count)
    if val_count + test_count >= total_images:
        test_count = max(0, total_images - val_count - 1)
        if val_count + test_count >= total_images:
            val_count = max(1, total_images - test_count - 1)

    split_by_image = {}
    for index, image_meta in enumerate(candidate_images):
        if index < val_count:
            split = "val"
        elif index < val_count + test_count:
            split = "test"
        else:
            split = "train"
        split_by_image[image_meta["id"]] = split

    if args.output.exists():
        shutil.rmtree(args.output)

    for split in ("train", "val", "test"):
        (args.output / "images" / split).mkdir(parents=True, exist_ok=True)
        (args.output / "labels" / split).mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    image_split_counts = Counter()
    target_image_counts = Counter()

    for image_meta in candidate_images:
        image_id = image_meta["id"]
        relative_source = Path(str(image_meta["file_name"]).replace("\\", "/"))
        source_image = args.images_root / relative_source
        if not source_image.exists():
            raise SystemExit(f"Missing TACO image on disk: {source_image}")

        split = split_by_image[image_id]
        image_split_counts[split] += 1
        target_name = safe_stem(image_id, relative_source.name)
        destination_image = args.output / "images" / split / target_name
        destination_label = args.output / "labels" / split / f"{Path(target_name).stem}.txt"

        hardlink_or_copy(source_image, destination_image, args.copy_mode)

        label_lines = [
            f"{box['class_id']} {box['yolo'][0]:.6f} {box['yolo'][1]:.6f} {box['yolo'][2]:.6f} {box['yolo'][3]:.6f}"
            for box in annotations_by_image.get(image_id, [])
        ]
        destination_label.write_text("\n".join(label_lines), encoding="utf-8")

        for class_name in {box["class_name"] for box in annotations_by_image.get(image_id, [])}:
            target_image_counts[class_name] += 1

        manifest_rows.append(
            {
                "image_id": image_id,
                "source_file": str(relative_source).replace("\\", "/"),
                "split": split,
                "box_count": len(label_lines),
                "output_image": destination_image.name,
                "output_label": destination_label.name,
            }
        )

    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest_output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["image_id", "source_file", "split", "box_count", "output_image", "output_label"],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    summary = {
        "source_annotations_total": len(annotations["annotations"]),
        "source_categories_total": len(categories),
        "images_total": len(images),
        "images_after_mapping": total_images,
        "target_classes": class_names,
        "target_box_counts": dict(target_class_counts),
        "target_image_counts": dict(target_image_counts),
        "skipped_source_categories": dict(skipped_class_counts),
        "split_image_counts": dict(image_split_counts),
        "copy_mode": args.copy_mode,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    write_yaml(args.output, class_names, args.yaml_output)

    print(f"Built remapped TACO dataset at: {args.output}")
    print(f"Dataset YAML: {args.yaml_output}")
    print(f"Manifest: {args.manifest_output}")
    print(f"Summary: {args.summary_output}")
    print(f"Images kept: {total_images}")
    print(f"Target box counts: {dict(target_class_counts)}")
    print(f"Target image counts: {dict(target_image_counts)}")
    print(f"Split image counts: {dict(image_split_counts)}")


if __name__ == "__main__":
    main()
