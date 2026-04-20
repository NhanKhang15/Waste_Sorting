from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.waste_sorter.annotator import gather_training_inventory  # noqa: E402
from backend.waste_sorter.materials import MATERIAL_ALIASES, load_material_classes  # noqa: E402


def suggest_label(relative_path: str, classes: list[str]) -> str:
    normalized_name = relative_path.lower()
    matches = []
    for keyword, class_name in MATERIAL_ALIASES.items():
        if keyword in normalized_name and class_name in classes and class_name not in matches:
            matches.append(class_name)
    return matches[0] if len(matches) == 1 else ""


def main() -> None:
    images_root = ROOT_DIR / "training_image"
    labels_root = ROOT_DIR / "training_labels"
    classes = load_material_classes(ROOT_DIR / "training" / "material_classes.txt")
    inventory = gather_training_inventory(images_root=images_root, labels_root=labels_root, classes=classes)

    output_path = ROOT_DIR / "training" / "material_manifest.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "path",
                "width",
                "height",
                "label_exists",
                "box_count",
                "suggested_material",
                "notes",
            ],
        )
        writer.writeheader()
        for item in inventory:
            writer.writerow(
                {
                    "path": item["path"],
                    "width": item["width"],
                    "height": item["height"],
                    "label_exists": item["label_exists"],
                    "box_count": item["box_count"],
                    "suggested_material": suggest_label(item["path"], classes),
                    "notes": "",
                }
            )

    print(f"Saved manifest to: {output_path}")
    print(f"Total images: {len(inventory)}")


if __name__ == "__main__":
    main()
