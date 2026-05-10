from app.core.errors import InvalidWasteQueryError
from dsl.parser import WasteQueryDslParser


def test_dsl_parser_builds_basic_waste_query_ast() -> None:
    parser = WasteQueryDslParser()

    ast = parser.parse("find me recyclable waste")

    assert ast.action == "find"
    assert ast.waste_group == "recyclable"
    assert ast.confidence_filter is None
    assert ast.label_filter is None
    assert ast.normalized_query() == "find recyclable waste"


def test_dsl_parser_supports_count_confidence_and_label_filter() -> None:
    parser = WasteQueryDslParser()

    ast = parser.parse(
        "count organic waste where confidence >= 0.65 and label = banana"
    )

    assert ast.action == "count"
    assert ast.waste_group == "organic"
    assert ast.confidence_filter is not None
    assert ast.confidence_filter.operator == ">="
    assert ast.confidence_filter.value == 0.65
    assert ast.label_filter is not None
    assert ast.label_filter.value == "banana"
    assert ast.to_tree().name == "WasteQuery"


def test_dsl_parser_accepts_quoted_multi_word_labels() -> None:
    parser = WasteQueryDslParser()

    ast = parser.parse('find recyclable waste where label = "wine glass"')

    assert ast.label_filter is not None
    assert ast.label_filter.value == "wine glass"
    assert ast.normalized_query() == 'find recyclable waste where label = "wine glass"'


def test_dsl_parser_rejects_out_of_range_confidence() -> None:
    parser = WasteQueryDslParser()

    try:
        parser.parse("find inorganic waste where confidence >= 1.2")
    except InvalidWasteQueryError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("InvalidWasteQueryError was not raised")
