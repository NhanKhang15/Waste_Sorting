from __future__ import annotations

from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream, TerminalNode
from antlr4.error.ErrorListener import ErrorListener

from antlr.generated.WasteQueryLexer import WasteQueryLexer
from antlr.generated.WasteQueryParser import WasteQueryParser
from antlr.generated.WasteQueryVisitor import WasteQueryVisitor
from app.core.errors import InvalidWasteQueryError
from dsl.ast import ConfidencePredicate, LabelPredicate, TokenInfo, WasteQueryAst


@dataclass(frozen=True)
class WasteQueryParseResult:
    """Full parse output: semantic AST, raw token stream, and academic derivation tree."""

    ast: WasteQueryAst
    tokens: tuple[TokenInfo, ...]
    formal_parse_tree: dict[str, object]


def _extract_tokens(token_stream: CommonTokenStream) -> tuple[TokenInfo, ...]:
    """Extract all non-EOF tokens from the filled token stream."""
    token_stream.fill()
    result: list[TokenInfo] = []
    for token in token_stream.tokens:
        if token.type == -1:  # Token.EOF
            break
        names = WasteQueryLexer.symbolicNames
        type_name = names[token.type] if 0 < token.type < len(names) else "UNKNOWN"
        result.append(TokenInfo(token_type=type_name, text=token.text))
    return tuple(result)


def _build_formal_parse_tree(ctx: object) -> dict[str, object]:
    """Recursively build an academic derivation tree from the ANTLR concrete syntax tree.

    Internal nodes correspond to grammar rule names (non-terminals).
    Leaf nodes correspond to lexer token types (terminals).
    """
    if isinstance(ctx, TerminalNode):
        token = ctx.symbol
        if token.type == -1:
            return {"name": "EOF", "is_terminal": True, "text": "<EOF>"}
        names = WasteQueryLexer.symbolicNames
        type_name = names[token.type] if 0 < token.type < len(names) else "UNKNOWN"
        return {"name": type_name, "is_terminal": True, "text": token.text}

    rule_names = WasteQueryParser.ruleNames
    rule_idx = ctx.getRuleIndex()
    rule_name = rule_names[rule_idx] if 0 <= rule_idx < len(rule_names) else "UNKNOWN"

    children: list[dict[str, object]] = []
    for i in range(ctx.getChildCount()):
        children.append(_build_formal_parse_tree(ctx.getChild(i)))

    node: dict[str, object] = {"name": rule_name, "is_terminal": False}
    if children:
        node["children"] = children
    return node

DSL_EXAMPLES = (
    "find me recyclable waste",
    "count organic waste where confidence >= 0.6",
    "recyclable waste",
    'find recyclable waste where confidence >= 0.8 and label = bottle',
    'find recyclable waste where label = "wine glass"',
)


class _WasteQueryErrorListener(ErrorListener):
    def syntaxError(
        self,
        recognizer,
        offendingSymbol,
        line,
        column,
        msg,
        e,
    ) -> None:
        del recognizer, line, column, msg, e
        token_text = getattr(offendingSymbol, "text", None)
        near = ""
        if token_text and token_text != "<EOF>":
            near = f" near '{token_text}'"
        examples = ", ".join(DSL_EXAMPLES)
        raise InvalidWasteQueryError(
            f"Unsupported DSL query{near}. Try one of: {examples}."
        )


class _AstBuilderVisitor(WasteQueryVisitor):
    def visitQuery(self, ctx):  # noqa: N802
        return self.visit(ctx.command())

    def visitCommand(self, ctx):  # noqa: N802
        action = self.visit(ctx.action()) if ctx.action() is not None else "find"
        waste_group = self.visit(ctx.wasteGroup())
        confidence_filter = None
        label_filter = None

        if ctx.whereClause() is not None:
            confidence_filter, label_filter = self.visit(ctx.whereClause())

        return WasteQueryAst(
            action=action,
            waste_group=waste_group,
            confidence_filter=confidence_filter,
            label_filter=label_filter,
        )

    def visitAction(self, ctx):  # noqa: N802
        return ctx.getText().lower()

    def visitWasteGroup(self, ctx):  # noqa: N802
        return ctx.getText().lower()

    def visitWhereClause(self, ctx):  # noqa: N802
        confidence_filter = None
        label_filter = None

        for predicate in ctx.predicate():
            value = self.visit(predicate)
            if isinstance(value, ConfidencePredicate):
                if confidence_filter is not None:
                    raise InvalidWasteQueryError(
                        "The DSL only supports one confidence filter per query."
                    )
                confidence_filter = value
                continue

            if isinstance(value, LabelPredicate):
                if label_filter is not None:
                    raise InvalidWasteQueryError(
                        "The DSL only supports one label filter per query."
                    )
                label_filter = value
                continue

        return confidence_filter, label_filter

    def visitPredicate(self, ctx):  # noqa: N802
        child = ctx.confidencePredicate() or ctx.labelPredicate()
        return self.visit(child)

    def visitConfidencePredicate(self, ctx):  # noqa: N802
        operator = self.visit(ctx.comparator())
        value = float(ctx.number().getText())
        if not 0 <= value <= 1:
            raise InvalidWasteQueryError(
                "Confidence values in the DSL must be between 0 and 1."
            )
        return ConfidencePredicate(operator=operator, value=value)

    def visitLabelPredicate(self, ctx):  # noqa: N802
        value = self.visit(ctx.labelValue())
        if not value:
            raise InvalidWasteQueryError("The DSL label filter cannot be empty.")
        return LabelPredicate(value=value)

    def visitLabelValue(self, ctx):  # noqa: N802
        if ctx.STRING() is not None:
            text = ctx.STRING().getText()
            value = text[1:-1]
            return value.replace('\\"', '"').replace("\\\\", "\\")
        return ctx.getText()

    def visitComparator(self, ctx):  # noqa: N802
        return ctx.getText()


class WasteQueryDslParser:
    def parse(self, raw_query: str) -> WasteQueryAst:
        source = raw_query.strip()
        if not source:
            examples = ", ".join(DSL_EXAMPLES)
            raise InvalidWasteQueryError(
                f"Query is required. Try one of: {examples}."
            )

        input_stream = InputStream(source)
        lexer = WasteQueryLexer(input_stream)
        error_listener = _WasteQueryErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        tokens = CommonTokenStream(lexer)
        parser = WasteQueryParser(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        tree = parser.query()
        ast = _AstBuilderVisitor().visit(tree)
        if ast is None:
            examples = ", ".join(DSL_EXAMPLES)
            raise InvalidWasteQueryError(
                f"Unsupported DSL query. Try one of: {examples}."
            )
        return ast

    def parse_full(self, raw_query: str) -> WasteQueryParseResult:
        """Parse a DSL query and return the AST, token stream, and formal derivation tree."""
        source = raw_query.strip()
        if not source:
            examples = ", ".join(DSL_EXAMPLES)
            raise InvalidWasteQueryError(
                f"Query is required. Try one of: {examples}."
            )

        input_stream = InputStream(source)
        lexer = WasteQueryLexer(input_stream)
        error_listener = _WasteQueryErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        parser = WasteQueryParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        cst = parser.query()
        ast = _AstBuilderVisitor().visit(cst)
        if ast is None:
            examples = ", ".join(DSL_EXAMPLES)
            raise InvalidWasteQueryError(
                f"Unsupported DSL query. Try one of: {examples}."
            )

        tokens = _extract_tokens(token_stream)
        formal_tree = _build_formal_parse_tree(cst)
        return WasteQueryParseResult(ast=ast, tokens=tokens, formal_parse_tree=formal_tree)

    @staticmethod
    def examples() -> list[str]:
        return list(DSL_EXAMPLES)
