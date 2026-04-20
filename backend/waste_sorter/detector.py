from __future__ import annotations

import uuid
from pathlib import Path

import cv2
from ultralytics import YOLO

from .keyword_classifier import WasteKeywordClassifier


GROUP_COLORS = {
    "organic": (44, 140, 76),
    "recyclable": (34, 119, 230),
    "inorganic": (46, 46, 211),
}


class QueryError(ValueError):
    pass


class WasteFinder:
    def __init__(self, model_path: str = "yolo26s.pt", confidence: float = 0.25) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self.classifier = WasteKeywordClassifier()
        self._model: YOLO | None = None
        self._class_names: dict[int, str] | None = None

    @property
    def model(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self.model_path)
            names = self._model.names
            if isinstance(names, dict):
                self._class_names = {int(key): str(value) for key, value in names.items()}
            else:
                self._class_names = {index: str(name) for index, name in enumerate(names)}
        return self._model

    @property
    def class_names(self) -> dict[int, str]:
        _ = self.model
        assert self._class_names is not None
        return self._class_names

    def find_matches(
        self,
        image_path: Path,
        query: str,
        crop_dir: Path,
        annotated_dir: Path,
    ) -> dict:
        search = self.classifier.parse_query(query)
        if search is None:
            examples = ", ".join(self.classifier.supported_queries())
            raise QueryError(f"Unsupported query. Try one of: {examples}.")

        source_image = cv2.imread(str(image_path))
        if source_image is None:
            raise ValueError("The uploaded image could not be read.")

        results = self.model.predict(source=str(image_path), conf=self.confidence, verbose=False)
        prediction = results[0]

        annotated_dir.mkdir(parents=True, exist_ok=True)
        crop_dir.mkdir(parents=True, exist_ok=True)

        matches = []
        for index, box in enumerate(prediction.boxes):
            class_id = int(box.cls.item())
            class_name = self.class_names[class_id]
            waste_group = self.classifier.classify_keyword(class_name)

            if waste_group != search.waste_group:
                continue

            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(source_image.shape[1], x2)
            y2 = min(source_image.shape[0], y2)

            crop = source_image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            crop_name = f"{search.waste_group}_{image_path.stem}_{index}_{uuid.uuid4().hex[:6]}.jpg"
            crop_path = crop_dir / crop_name
            cv2.imwrite(str(crop_path), crop)

            matches.append(
                {
                    "class_name": class_name,
                    "waste_group": waste_group,
                    "confidence": round(float(box.conf.item()), 3),
                    "crop_url": f"/static/crops/{crop_name}",
                    "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                }
            )

        annotated_name = f"annotated_{image_path.stem}_{uuid.uuid4().hex[:8]}.jpg"
        annotated_path = annotated_dir / annotated_name
        annotated_image = self.draw_filtered_boxes(source_image, matches)
        cv2.imwrite(str(annotated_path), annotated_image)

        return {
            "query": query,
            "mode": "waste_group",
            "engine": "coco80_rule_map",
            "label": search.waste_group,
            "count": len(matches),
            "targets": sorted(search.allowed_keywords),
            "annotated_image": f"/static/annotated/{annotated_name}",
            "matches": matches,
        }

    def draw_filtered_boxes(self, source_image, matches: list[dict]):
        annotated = source_image.copy()
        for match in matches:
            color = GROUP_COLORS.get(match["waste_group"], (0, 180, 0))
            x1 = match["box"]["x1"]
            y1 = match["box"]["y1"]
            x2 = match["box"]["x2"]
            y2 = match["box"]["y2"]
            label = f"{match['class_name']} -> {match['waste_group']}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            (text_width, text_height), baseline = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                2,
            )
            label_y = max(y1 - text_height - baseline - 8, 0)
            cv2.rectangle(
                annotated,
                (x1, label_y),
                (x1 + text_width + 10, label_y + text_height + baseline + 8),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 5, label_y + text_height + 1),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
        return annotated
