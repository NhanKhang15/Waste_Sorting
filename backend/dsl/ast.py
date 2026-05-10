from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenInfo:
    """A single token from the DSL lexer: type name + raw text."""

    token_type: str
    text: str

    def to_dict(self) -> dict[str, str]:
        return {"type": self.token_type, "text": self.text}


def _format_number(value: float) -> str:
    rendered = f"{value:.4f}".rstrip("0").rstrip(".")
    return rendered or "0"


@dataclass(frozen=True, slots=True)
class ParseTreeNode:
    name: str
    children: tuple["ParseTreeNode", ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {"name": self.name}
        if self.children:
            payload["children"] = [child.to_dict() for child in self.children]
        return payload


@dataclass(frozen=True, slots=True)
class ConfidencePredicate:
    operator: str
    value: float

    def matches(self, confidence: float) -> bool:
        if self.operator == ">=":
            return confidence >= self.value
        if self.operator == ">":
            return confidence > self.value
        if self.operator == "<=":
            return confidence <= self.value
        if self.operator == "<":
            return confidence < self.value
        if self.operator == "==":
            return confidence == self.value
        raise ValueError(f"Unsupported confidence operator: {self.operator}")

    def render(self) -> str:
        return f"confidence {self.operator} {_format_number(self.value)}"

    def to_tree(self) -> ParseTreeNode:
        return ParseTreeNode(
            name="ConfidenceFilter",
            children=(
                ParseTreeNode(name=f"operator={self.operator}"),
                ParseTreeNode(name=f"value={_format_number(self.value)}"),
            ),
        )


@dataclass(frozen=True, slots=True)
class LabelPredicate:
    value: str

    def render(self) -> str:
        if " " in self.value:
            return f'label = "{self.value}"'
        return f"label = {self.value}"

    def to_tree(self) -> ParseTreeNode:
        return ParseTreeNode(
            name="LabelFilter",
            children=(ParseTreeNode(name=f"value={self.value}"),),
        )


@dataclass(frozen=True, slots=True)
class WasteQueryAst:
    action: str
    waste_group: str
    confidence_filter: ConfidencePredicate | None = None
    label_filter: LabelPredicate | None = None

    def normalized_query(self) -> str:
        query = f"{self.action} {self.waste_group} waste"
        predicates: list[str] = []
        if self.confidence_filter is not None:
            predicates.append(self.confidence_filter.render())
        if self.label_filter is not None:
            predicates.append(self.label_filter.render())

        if not predicates:
            return query
        return f"{query} where {' and '.join(predicates)}"

    def to_tree(self) -> ParseTreeNode:
        children = [
            ParseTreeNode(
                name="Action",
                children=(ParseTreeNode(name=self.action),),
            ),
            ParseTreeNode(
                name="WasteGroup",
                children=(ParseTreeNode(name=self.waste_group),),
            ),
        ]
        if self.confidence_filter is not None:
            children.append(self.confidence_filter.to_tree())
        if self.label_filter is not None:
            children.append(self.label_filter.to_tree())

        return ParseTreeNode(name="WasteQuery", children=tuple(children))

    def to_expression(self, allowed_keywords: frozenset[str]) -> "WasteQueryExpression":
        """Build a GoF Interpreter expression tree from this AST."""
        from dsl.interpreter import (
            ActionExpression,
            ConfidenceFilterExpression,
            LabelFilterExpression,
            WasteGroupExpression,
            WasteQueryExpression,
        )

        filters = []
        if self.confidence_filter is not None:
            filters.append(
                ConfidenceFilterExpression(
                    self.confidence_filter.operator,
                    self.confidence_filter.value,
                )
            )
        if self.label_filter is not None:
            filters.append(LabelFilterExpression(self.label_filter.value))

        return WasteQueryExpression(
            ActionExpression(self.action),
            WasteGroupExpression(),
            filters,
        )
