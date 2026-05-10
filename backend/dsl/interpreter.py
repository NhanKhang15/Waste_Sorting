from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from dsl.functional import apply_filters, make_confidence_filter, make_group_filter, make_label_filter


@dataclass
class InterpreterContext:
    """Execution context passed to every expression during interpretation."""

    detections: list[Any]
    normalize: Callable[[str], str]
    allowed_keywords: frozenset[str]
    group: str


class AbstractExpression(ABC):
    """GoF Interpreter Pattern — abstract base for all DSL expressions."""

    @abstractmethod
    def interpret(self, context: InterpreterContext) -> Any:
        ...


class ActionExpression(AbstractExpression):
    """Terminal: represents the query action keyword (find / count)."""

    def __init__(self, action: str) -> None:
        self._action = action

    def interpret(self, context: InterpreterContext) -> str:
        return self._action


class WasteGroupExpression(AbstractExpression):
    """Terminal: filters detections belonging to the target waste group."""

    def interpret(self, context: InterpreterContext) -> list[Any]:
        group_filter = make_group_filter(
            context.normalize,
            context.group,
            context.allowed_keywords,
        )
        return list(filter(group_filter, context.detections))


class ConfidenceFilterExpression(AbstractExpression):
    """Terminal: a confidence threshold predicate for the WHERE clause."""

    def __init__(self, operator: str, value: float) -> None:
        self._operator = operator
        self._value = value

    def interpret(self, context: InterpreterContext) -> Callable[[Any], bool]:
        return make_confidence_filter(self._operator, self._value)


class LabelFilterExpression(AbstractExpression):
    """Terminal: a label equality predicate for the WHERE clause."""

    def __init__(self, label: str) -> None:
        self._label = label

    def interpret(self, context: InterpreterContext) -> Callable[[Any], bool]:
        return make_label_filter(context.normalize, self._label)


class WasteQueryExpression(AbstractExpression):
    """Non-terminal: composes group, action, and filter sub-expressions."""

    def __init__(
        self,
        action: ActionExpression,
        group: WasteGroupExpression,
        filters: list[AbstractExpression],
    ) -> None:
        self._action = action
        self._group = group
        self._filters = filters

    def interpret(self, context: InterpreterContext) -> dict[str, Any]:
        action = self._action.interpret(context)
        candidates = self._group.interpret(context)

        filter_context = InterpreterContext(
            detections=candidates,
            normalize=context.normalize,
            allowed_keywords=context.allowed_keywords,
            group=context.group,
        )
        predicates = [f.interpret(filter_context) for f in self._filters]
        matches = apply_filters(candidates, predicates)

        return {
            "action": action,
            "matches": matches,
            "count": len(matches),
        }
