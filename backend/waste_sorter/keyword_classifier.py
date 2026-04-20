from __future__ import annotations

import re
from dataclasses import dataclass


WASTE_GROUP_KEYWORDS = {
    "organic": {
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot dog",
        "pizza",
        "donut",
        "cake",
        "potted plant",
    },
    "recyclable": {
        "bottle",
        "wine glass",
        "cup",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "book",
        "kite",
        "vase",
        "scissors",
    },
    "inorganic": {
        "backpack",
        "umbrella",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis",
        "snowboard",
        "sports ball",
        "baseball bat",
        "baseball glove",
        "skateboard",
        "surfboard",
        "tennis racket",
        "chair",
        "couch",
        "bed",
        "dining table",
        "toilet",
        "tv",
        "laptop",
        "mouse",
        "remote",
        "keyboard",
        "cell phone",
        "microwave",
        "oven",
        "toaster",
        "sink",
        "refrigerator",
        "clock",
        "teddy bear",
        "hair drier",
        "toothbrush",
    },
}

QUERY_ALIASES = {
    "find me organic waste": "organic",
    "organic waste": "organic",
    "organic": "organic",
    "find me recyclable waste": "recyclable",
    "recyclable waste": "recyclable",
    "recyclable": "recyclable",
    "find me inorganic waste": "inorganic",
    "inorganic waste": "inorganic",
    "inorganic": "inorganic",
}


@dataclass(frozen=True)
class WasteQuery:
    raw_query: str
    waste_group: str
    allowed_keywords: set[str]


class WasteKeywordClassifier:
    def __init__(self) -> None:
        self.group_keywords = {group: set(values) for group, values in WASTE_GROUP_KEYWORDS.items()}
        self.keyword_to_group = {
            keyword: group
            for group, keywords in self.group_keywords.items()
            for keyword in keywords
        }

    def normalize(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def parse_query(self, raw_query: str) -> WasteQuery | None:
        normalized = self.normalize(raw_query)
        waste_group = QUERY_ALIASES.get(normalized)
        if waste_group is None:
            return None
        return WasteQuery(
            raw_query=raw_query,
            waste_group=waste_group,
            allowed_keywords=self.group_keywords[waste_group],
        )

    def classify_keyword(self, keyword: str) -> str | None:
        return self.keyword_to_group.get(self.normalize(keyword))

    def supported_queries(self) -> list[str]:
        return [
            "find me organic waste",
            "find me recyclable waste",
            "find me inorganic waste",
        ]

    def supported_groups(self) -> list[str]:
        return list(self.group_keywords)
