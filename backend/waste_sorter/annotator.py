from __future__ import annotations

from pathlib import Path

from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def resolve_training_image_path(images_root: Path, relative_path: str) -> Path:
    if not relative_path:
        raise ValueError("Thiếu đường dẫn ảnh.")

    root = images_root.resolve()
    image_path = (root / relative_path).resolve()
    if root != image_path and root not in image_path.parents:
        raise ValueError("Đường dẫn ảnh không hợp lệ.")
    if not image_path.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {relative_path}")
    return image_path


def resolve_training_label_path(images_root: Path, labels_root: Path, relative_path: str) -> Path:
    image_path = resolve_training_image_path(images_root, relative_path)
    relative_image = image_path.relative_to(images_root.resolve())
    return (labels_root.resolve() / relative_image).with_suffix(".txt")


def iter_training_images(images_root: Path) -> list[Path]:
    if not images_root.exists():
        return []

    return sorted(
        [
            path
            for path in images_root.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )


def _load_image_size(image_path: Path) -> tuple[int, int]:
    with Image.open(image_path) as image:
        return image.size


def load_annotations(
    image_path: Path,
    label_path: Path,
    classes: list[str],
    relative_path: str,
) -> dict:
    width, height = _load_image_size(image_path)
    annotations = []

    if label_path.exists():
        for index, raw_line in enumerate(label_path.read_text(encoding="utf-8").splitlines()):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            center_x, center_y, box_width, box_height = [float(value) for value in parts[1:]]
            x1 = max(0.0, (center_x - box_width / 2) * width)
            y1 = max(0.0, (center_y - box_height / 2) * height)
            x2 = min(float(width), (center_x + box_width / 2) * width)
            y2 = min(float(height), (center_y + box_height / 2) * height)
            class_name = classes[class_id] if 0 <= class_id < len(classes) else f"class_{class_id}"

            annotations.append(
                {
                    "id": index,
                    "class_name": class_name,
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2),
                }
            )

    return {
        "image": relative_path,
        "width": width,
        "height": height,
        "label_exists": label_path.exists(),
        "box_count": len(annotations),
        "annotations": annotations,
    }


def save_annotations(
    image_path: Path,
    label_path: Path,
    classes: list[str],
    annotations: list[dict],
    relative_path: str,
) -> dict:
    width, height = _load_image_size(image_path)
    class_to_index = {class_name: index for index, class_name in enumerate(classes)}
    lines = []

    for annotation in annotations:
        class_name = str(annotation.get("class_name", "")).strip()
        if class_name not in class_to_index:
            raise ValueError(f"Class '{class_name}' không có trong material_classes.txt")

        x1 = max(0.0, min(float(annotation.get("x1", 0.0)), float(width)))
        y1 = max(0.0, min(float(annotation.get("y1", 0.0)), float(height)))
        x2 = max(0.0, min(float(annotation.get("x2", 0.0)), float(width)))
        y2 = max(0.0, min(float(annotation.get("y2", 0.0)), float(height)))

        if x2 <= x1 or y2 <= y1:
            continue

        center_x = ((x1 + x2) / 2) / width
        center_y = ((y1 + y2) / 2) / height
        box_width = (x2 - x1) / width
        box_height = (y2 - y1) / height

        lines.append(
            f"{class_to_index[class_name]} "
            f"{center_x:.6f} {center_y:.6f} {box_width:.6f} {box_height:.6f}"
        )

    label_path.parent.mkdir(parents=True, exist_ok=True)
    label_path.write_text("\n".join(lines), encoding="utf-8")

    return load_annotations(
        image_path=image_path,
        label_path=label_path,
        classes=classes,
        relative_path=relative_path,
    )


def gather_training_inventory(
    images_root: Path,
    labels_root: Path,
    classes: list[str],
) -> list[dict]:
    inventory = []
    for image_path in iter_training_images(images_root):
        relative_path = str(image_path.relative_to(images_root.resolve())).replace("\\", "/")
        label_path = resolve_training_label_path(images_root, labels_root, relative_path)
        annotation_payload = load_annotations(
            image_path=image_path,
            label_path=label_path,
            classes=classes,
            relative_path=relative_path,
        )
        inventory.append(
            {
                "path": relative_path,
                "width": annotation_payload["width"],
                "height": annotation_payload["height"],
                "label_exists": annotation_payload["label_exists"],
                "box_count": annotation_payload["box_count"],
            }
        )
    return inventory
