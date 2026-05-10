# Generated from WasteQuery.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .WasteQueryParser import WasteQueryParser
else:
    from WasteQueryParser import WasteQueryParser

# This class defines a complete generic visitor for a parse tree produced by WasteQueryParser.

class WasteQueryVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by WasteQueryParser#query.
    def visitQuery(self, ctx:WasteQueryParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#command.
    def visitCommand(self, ctx:WasteQueryParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#action.
    def visitAction(self, ctx:WasteQueryParser.ActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#wasteGroup.
    def visitWasteGroup(self, ctx:WasteQueryParser.WasteGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#whereClause.
    def visitWhereClause(self, ctx:WasteQueryParser.WhereClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#predicate.
    def visitPredicate(self, ctx:WasteQueryParser.PredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#confidencePredicate.
    def visitConfidencePredicate(self, ctx:WasteQueryParser.ConfidencePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#labelPredicate.
    def visitLabelPredicate(self, ctx:WasteQueryParser.LabelPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#labelComparator.
    def visitLabelComparator(self, ctx:WasteQueryParser.LabelComparatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#comparator.
    def visitComparator(self, ctx:WasteQueryParser.ComparatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#number.
    def visitNumber(self, ctx:WasteQueryParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by WasteQueryParser#labelValue.
    def visitLabelValue(self, ctx:WasteQueryParser.LabelValueContext):
        return self.visitChildren(ctx)



del WasteQueryParser