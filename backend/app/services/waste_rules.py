from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from app.core.errors import InvalidWasteQueryError
from app.schemas.yolov26 import DetectionObject, DetectionResponse
from dsl.ast import TokenInfo, WasteQueryAst
from dsl.interpreter import InterpreterContext
from dsl.parser import WasteQueryDslParser

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

@dataclass(frozen=True)
class ParsedWasteQuery:
    raw_query: str
    normalized_query: str
    query_action: str
    waste_group: str
    allowed_keywords: tuple[str, ...]
    ast: WasteQueryAst
    parse_tree: dict[str, object]           # semantic AST tree (backward-compat)
    formal_parse_tree: dict[str, object]    # academic derivation tree from ANTLR CST
    tokens: tuple[TokenInfo, ...]           # token stream from lexer
    confidence_operator: str | None
    minimum_confidence: float | None
    label_filter: str | None


class WasteRuleMatcher:
    def __init__(self, parser: WasteQueryDslParser | None = None) -> None:
        self._group_keywords = {
            group: tuple(sorted(values))
            for group, values in WASTE_GROUP_KEYWORDS.items()
        }
        self._keyword_to_group = {
            keyword: group
            for group, keywords in self._group_keywords.items()
            for keyword in keywords
        }
        self._keyword_to_group.update({group: group for group in self._group_keywords})
        self._parser = parser or WasteQueryDslParser()

    @staticmethod
    def normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def supported_groups(self) -> list[str]:
        return list(self._group_keywords)

    def supported_queries(self) -> list[str]:
        return [
            "find me organic waste",
            "find me recyclable waste",
            "find me inorganic waste",
        ]

    def supported_dsl_examples(self) -> list[str]:
        return self._parser.examples()

    def group_keywords(self) -> dict[str, list[str]]:
        return {
            group: list(keywords)
            for group, keywords in self._group_keywords.items()
        }

    def parse_query(self, raw_query: str) -> ParsedWasteQuery:
        parse_result = self._parser.parse_full(raw_query)
        ast = parse_result.ast
        waste_group = ast.waste_group
        if waste_group not in self._group_keywords:
            examples = ", ".join(self.supported_dsl_examples())
            raise InvalidWasteQueryError(
                f"Unsupported waste group. Try one of: {examples}."
            )

        confidence_filter = ast.confidence_filter

        return ParsedWasteQuery(
            raw_query=raw_query,
            normalized_query=ast.normalized_query(),
            query_action=ast.action,
            waste_group=waste_group,
            allowed_keywords=self._group_keywords[waste_group],
            ast=ast,
            parse_tree=ast.to_tree().to_dict(),
            formal_parse_tree=parse_result.formal_parse_tree,
            tokens=parse_result.tokens,
            confidence_operator=confidence_filter.operator if confidence_filter else None,
            minimum_confidence=confidence_filter.value if confidence_filter else None,
            label_filter=ast.label_filter.value if ast.label_filter else None,
        )

    def classify_label(self, label: str) -> str | None:
        return self._keyword_to_group.get(self.normalize(label))

    def match_detections(
        self,
        *,
        query: str,
        response: DetectionResponse,
    ) -> tuple[ParsedWasteQuery, list[DetectionObject]]:
        parsed_query = self.parse_query(query)
        matches = self.match_parsed_query(
            parsed_query=parsed_query,
            response=response,
        )
        return parsed_query, matches

    def match_parsed_query(
        self,
        *,
        parsed_query: ParsedWasteQuery,
        response: DetectionResponse,
    ) -> list[DetectionObject]:
        expression = parsed_query.ast.to_expression(
            frozenset(parsed_query.allowed_keywords)
        )
        context = InterpreterContext(
            detections=response.detections,
            normalize=self.normalize,
            allowed_keywords=frozenset(parsed_query.allowed_keywords),
            group=parsed_query.waste_group,
        )
        result = expression.interpret(context)
        return result["matches"]
