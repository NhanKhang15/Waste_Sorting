# Generated from WasteQuery.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,21,81,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,1,0,1,1,1,
        1,3,1,30,8,1,1,1,1,1,3,1,34,8,1,1,1,3,1,37,8,1,1,1,1,1,3,1,41,8,
        1,1,1,3,1,44,8,1,3,1,46,8,1,1,2,1,2,1,3,1,3,1,4,1,4,1,4,1,4,5,4,
        56,8,4,10,4,12,4,59,9,4,1,5,1,5,3,5,63,8,5,1,6,1,6,1,6,1,6,1,7,1,
        7,1,7,1,7,1,8,1,8,1,9,1,9,1,10,1,10,1,11,1,11,1,11,0,0,12,0,2,4,
        6,8,10,12,14,16,18,20,22,0,5,1,0,1,2,1,0,9,11,1,0,16,17,1,0,12,16,
        1,0,19,20,76,0,24,1,0,0,0,2,45,1,0,0,0,4,47,1,0,0,0,6,49,1,0,0,0,
        8,51,1,0,0,0,10,62,1,0,0,0,12,64,1,0,0,0,14,68,1,0,0,0,16,72,1,0,
        0,0,18,74,1,0,0,0,20,76,1,0,0,0,22,78,1,0,0,0,24,25,3,2,1,0,25,26,
        5,0,0,1,26,1,1,0,0,0,27,29,3,4,2,0,28,30,5,3,0,0,29,28,1,0,0,0,29,
        30,1,0,0,0,30,31,1,0,0,0,31,33,3,6,3,0,32,34,5,4,0,0,33,32,1,0,0,
        0,33,34,1,0,0,0,34,36,1,0,0,0,35,37,3,8,4,0,36,35,1,0,0,0,36,37,
        1,0,0,0,37,46,1,0,0,0,38,40,3,6,3,0,39,41,5,4,0,0,40,39,1,0,0,0,
        40,41,1,0,0,0,41,43,1,0,0,0,42,44,3,8,4,0,43,42,1,0,0,0,43,44,1,
        0,0,0,44,46,1,0,0,0,45,27,1,0,0,0,45,38,1,0,0,0,46,3,1,0,0,0,47,
        48,7,0,0,0,48,5,1,0,0,0,49,50,7,1,0,0,50,7,1,0,0,0,51,52,5,5,0,0,
        52,57,3,10,5,0,53,54,5,6,0,0,54,56,3,10,5,0,55,53,1,0,0,0,56,59,
        1,0,0,0,57,55,1,0,0,0,57,58,1,0,0,0,58,9,1,0,0,0,59,57,1,0,0,0,60,
        63,3,12,6,0,61,63,3,14,7,0,62,60,1,0,0,0,62,61,1,0,0,0,63,11,1,0,
        0,0,64,65,5,7,0,0,65,66,3,18,9,0,66,67,3,20,10,0,67,13,1,0,0,0,68,
        69,5,8,0,0,69,70,3,16,8,0,70,71,3,22,11,0,71,15,1,0,0,0,72,73,7,
        2,0,0,73,17,1,0,0,0,74,75,7,3,0,0,75,19,1,0,0,0,76,77,5,18,0,0,77,
        21,1,0,0,0,78,79,7,4,0,0,79,23,1,0,0,0,8,29,33,36,40,43,45,57,62
    ]

class WasteQueryParser ( Parser ):

    grammarFileName = "WasteQuery.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'>='", "'>'", "'<='", "'<'", "'=='", "'='" ]

    symbolicNames = [ "<INVALID>", "FIND", "COUNT", "ME", "WASTE", "WHERE", 
                      "AND", "CONFIDENCE", "LABEL", "ORGANIC", "RECYCLABLE", 
                      "INORGANIC", "GTE", "GT", "LTE", "LT", "EQ", "ASSIGN", 
                      "DECIMAL", "STRING", "IDENTIFIER", "WS" ]

    RULE_query = 0
    RULE_command = 1
    RULE_action = 2
    RULE_wasteGroup = 3
    RULE_whereClause = 4
    RULE_predicate = 5
    RULE_confidencePredicate = 6
    RULE_labelPredicate = 7
    RULE_labelComparator = 8
    RULE_comparator = 9
    RULE_number = 10
    RULE_labelValue = 11

    ruleNames =  [ "query", "command", "action", "wasteGroup", "whereClause", 
                   "predicate", "confidencePredicate", "labelPredicate", 
                   "labelComparator", "comparator", "number", "labelValue" ]

    EOF = Token.EOF
    FIND=1
    COUNT=2
    ME=3
    WASTE=4
    WHERE=5
    AND=6
    CONFIDENCE=7
    LABEL=8
    ORGANIC=9
    RECYCLABLE=10
    INORGANIC=11
    GTE=12
    GT=13
    LTE=14
    LT=15
    EQ=16
    ASSIGN=17
    DECIMAL=18
    STRING=19
    IDENTIFIER=20
    WS=21

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def command(self):
            return self.getTypedRuleContext(WasteQueryParser.CommandContext,0)


        def EOF(self):
            return self.getToken(WasteQueryParser.EOF, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_query

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery" ):
                return visitor.visitQuery(self)
            else:
                return visitor.visitChildren(self)




    def query(self):

        localctx = WasteQueryParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.command()
            self.state = 25
            self.match(WasteQueryParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def action(self):
            return self.getTypedRuleContext(WasteQueryParser.ActionContext,0)


        def wasteGroup(self):
            return self.getTypedRuleContext(WasteQueryParser.WasteGroupContext,0)


        def ME(self):
            return self.getToken(WasteQueryParser.ME, 0)

        def WASTE(self):
            return self.getToken(WasteQueryParser.WASTE, 0)

        def whereClause(self):
            return self.getTypedRuleContext(WasteQueryParser.WhereClauseContext,0)


        def getRuleIndex(self):
            return WasteQueryParser.RULE_command

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand" ):
                return visitor.visitCommand(self)
            else:
                return visitor.visitChildren(self)




    def command(self):

        localctx = WasteQueryParser.CommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.state = 45
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1, 2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 27
                self.action()
                self.state = 29
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 28
                    self.match(WasteQueryParser.ME)


                self.state = 31
                self.wasteGroup()
                self.state = 33
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 32
                    self.match(WasteQueryParser.WASTE)


                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 35
                    self.whereClause()


                pass
            elif token in [9, 10, 11]:
                self.enterOuterAlt(localctx, 2)
                self.state = 38
                self.wasteGroup()
                self.state = 40
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 39
                    self.match(WasteQueryParser.WASTE)


                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 42
                    self.whereClause()


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ActionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FIND(self):
            return self.getToken(WasteQueryParser.FIND, 0)

        def COUNT(self):
            return self.getToken(WasteQueryParser.COUNT, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_action

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAction" ):
                return visitor.visitAction(self)
            else:
                return visitor.visitChildren(self)




    def action(self):

        localctx = WasteQueryParser.ActionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_action)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            _la = self._input.LA(1)
            if not(_la==1 or _la==2):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WasteGroupContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ORGANIC(self):
            return self.getToken(WasteQueryParser.ORGANIC, 0)

        def RECYCLABLE(self):
            return self.getToken(WasteQueryParser.RECYCLABLE, 0)

        def INORGANIC(self):
            return self.getToken(WasteQueryParser.INORGANIC, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_wasteGroup

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWasteGroup" ):
                return visitor.visitWasteGroup(self)
            else:
                return visitor.visitChildren(self)




    def wasteGroup(self):

        localctx = WasteQueryParser.WasteGroupContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_wasteGroup)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 3584) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(WasteQueryParser.WHERE, 0)

        def predicate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(WasteQueryParser.PredicateContext)
            else:
                return self.getTypedRuleContext(WasteQueryParser.PredicateContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(WasteQueryParser.AND)
            else:
                return self.getToken(WasteQueryParser.AND, i)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_whereClause

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhereClause" ):
                return visitor.visitWhereClause(self)
            else:
                return visitor.visitChildren(self)




    def whereClause(self):

        localctx = WasteQueryParser.WhereClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_whereClause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(WasteQueryParser.WHERE)
            self.state = 52
            self.predicate()
            self.state = 57
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 53
                self.match(WasteQueryParser.AND)
                self.state = 54
                self.predicate()
                self.state = 59
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PredicateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def confidencePredicate(self):
            return self.getTypedRuleContext(WasteQueryParser.ConfidencePredicateContext,0)


        def labelPredicate(self):
            return self.getTypedRuleContext(WasteQueryParser.LabelPredicateContext,0)


        def getRuleIndex(self):
            return WasteQueryParser.RULE_predicate

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPredicate" ):
                return visitor.visitPredicate(self)
            else:
                return visitor.visitChildren(self)




    def predicate(self):

        localctx = WasteQueryParser.PredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_predicate)
        try:
            self.state = 62
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 60
                self.confidencePredicate()
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 2)
                self.state = 61
                self.labelPredicate()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConfidencePredicateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONFIDENCE(self):
            return self.getToken(WasteQueryParser.CONFIDENCE, 0)

        def comparator(self):
            return self.getTypedRuleContext(WasteQueryParser.ComparatorContext,0)


        def number(self):
            return self.getTypedRuleContext(WasteQueryParser.NumberContext,0)


        def getRuleIndex(self):
            return WasteQueryParser.RULE_confidencePredicate

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConfidencePredicate" ):
                return visitor.visitConfidencePredicate(self)
            else:
                return visitor.visitChildren(self)




    def confidencePredicate(self):

        localctx = WasteQueryParser.ConfidencePredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_confidencePredicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.match(WasteQueryParser.CONFIDENCE)
            self.state = 65
            self.comparator()
            self.state = 66
            self.number()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LabelPredicateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LABEL(self):
            return self.getToken(WasteQueryParser.LABEL, 0)

        def labelComparator(self):
            return self.getTypedRuleContext(WasteQueryParser.LabelComparatorContext,0)


        def labelValue(self):
            return self.getTypedRuleContext(WasteQueryParser.LabelValueContext,0)


        def getRuleIndex(self):
            return WasteQueryParser.RULE_labelPredicate

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabelPredicate" ):
                return visitor.visitLabelPredicate(self)
            else:
                return visitor.visitChildren(self)




    def labelPredicate(self):

        localctx = WasteQueryParser.LabelPredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_labelPredicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(WasteQueryParser.LABEL)
            self.state = 69
            self.labelComparator()
            self.state = 70
            self.labelValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LabelComparatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSIGN(self):
            return self.getToken(WasteQueryParser.ASSIGN, 0)

        def EQ(self):
            return self.getToken(WasteQueryParser.EQ, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_labelComparator

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabelComparator" ):
                return visitor.visitLabelComparator(self)
            else:
                return visitor.visitChildren(self)




    def labelComparator(self):

        localctx = WasteQueryParser.LabelComparatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_labelComparator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            _la = self._input.LA(1)
            if not(_la==16 or _la==17):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GTE(self):
            return self.getToken(WasteQueryParser.GTE, 0)

        def GT(self):
            return self.getToken(WasteQueryParser.GT, 0)

        def LTE(self):
            return self.getToken(WasteQueryParser.LTE, 0)

        def LT(self):
            return self.getToken(WasteQueryParser.LT, 0)

        def EQ(self):
            return self.getToken(WasteQueryParser.EQ, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_comparator

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparator" ):
                return visitor.visitComparator(self)
            else:
                return visitor.visitChildren(self)




    def comparator(self):

        localctx = WasteQueryParser.ComparatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_comparator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 126976) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DECIMAL(self):
            return self.getToken(WasteQueryParser.DECIMAL, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_number

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber" ):
                return visitor.visitNumber(self)
            else:
                return visitor.visitChildren(self)




    def number(self):

        localctx = WasteQueryParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_number)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self.match(WasteQueryParser.DECIMAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LabelValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(WasteQueryParser.STRING, 0)

        def IDENTIFIER(self):
            return self.getToken(WasteQueryParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return WasteQueryParser.RULE_labelValue

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabelValue" ):
                return visitor.visitLabelValue(self)
            else:
                return visitor.visitChildren(self)




    def labelValue(self):

        localctx = WasteQueryParser.LabelValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_labelValue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            _la = self._input.LA(1)
            if not(_la==19 or _la==20):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





