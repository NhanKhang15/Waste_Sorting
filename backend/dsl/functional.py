from __future__ import annotations

from functools import reduce
from typing import Callable, TypeVar

T = TypeVar("T")


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition: compose(f, g)(x) == f(g(x))."""
    if not fns:
        return lambda x: x
    return reduce(lambda f, g: lambda x: f(g(x)), fns)


def pipeline(*fns: Callable) -> Callable:
    """Left-to-right function composition: pipeline(f, g)(x) == g(f(x))."""
    if not fns:
        return lambda x: x
    return reduce(lambda f, g: lambda x: g(f(x)), fns)


def make_confidence_filter(operator: str, threshold: float) -> Callable[[object], bool]:
    """Curried: returns a predicate for confidence-based filtering."""
    _ops: dict[str, Callable[[float, float], bool]] = {
        ">=": lambda c, t: c >= t,
        ">": lambda c, t: c > t,
        "<=": lambda c, t: c <= t,
        "<": lambda c, t: c < t,
        "==": lambda c, t: c == t,
    }
    op_fn = _ops.get(operator, lambda _c, _t: True)
    return lambda det: op_fn(det.confidence, threshold)


def make_group_filter(
    normalize: Callable[[str], str],
    group: str,
    allowed_keywords: frozenset[str],
) -> Callable[[object], bool]:
    """Curried: returns a predicate for waste-group filtering."""
    return lambda det: (
        normalize(det.label) in allowed_keywords
        or normalize(det.label) == group
    )


def make_label_filter(
    normalize: Callable[[str], str],
    label: str,
) -> Callable[[object], bool]:
    """Curried: returns a predicate for label equality filtering."""
    normalized = normalize(label)
    return lambda det: normalize(det.label) == normalized


def apply_filters(
    detections: list,
    filters: list[Callable[[object], bool]],
) -> list:
    """Apply a pipeline of predicate filters using reduce + filter."""
    if not filters:
        return list(detections)
    combined = reduce(lambda f, g: lambda x: f(x) and g(x), filters)
    return list(filter(combined, detections))
