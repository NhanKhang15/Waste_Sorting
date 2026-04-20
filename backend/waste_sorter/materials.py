from __future__ import annotations

from pathlib import Path


DEFAULT_MATERIAL_CLASSES = [
    "plastic",
    "glass",
    "wood",
    "metal",
    "paper",
    "organic",
    "ewaste",
]

MATERIAL_ALIASES = {
    "nhua": "plastic",
    "chai nhua": "plastic",
    "tui nilon": "plastic",
    "nilon": "plastic",
    "plastic": "plastic",
    "thuy tinh": "glass",
    "glass": "glass",
    "go": "wood",
    "wood": "wood",
    "kim loai": "metal",
    "metal": "metal",
    "giay": "paper",
    "paper": "paper",
    "huu co": "organic",
    "organic": "organic",
    "dien tu": "ewaste",
    "ewaste": "ewaste",
}


def load_material_classes(path: str | Path | None = None) -> list[str]:
    if path is not None:
        file_path = Path(path)
        if file_path.exists():
            items = [
                line.strip()
                for line in file_path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            if items:
                return items
    return DEFAULT_MATERIAL_CLASSES.copy()
