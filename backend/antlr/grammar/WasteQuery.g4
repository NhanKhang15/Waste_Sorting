grammar WasteQuery;

query
    : command EOF
    ;

command
    : action ME? wasteGroup WASTE? whereClause?
    | wasteGroup WASTE? whereClause?
    ;

action
    : FIND
    | COUNT
    ;

wasteGroup
    : ORGANIC
    | RECYCLABLE
    | INORGANIC
    ;

whereClause
    : WHERE predicate (AND predicate)*
    ;

predicate
    : confidencePredicate
    | labelPredicate
    ;

confidencePredicate
    : CONFIDENCE comparator number
    ;

labelPredicate
    : LABEL labelComparator labelValue
    ;

labelComparator
    : ASSIGN
    | EQ
    ;

comparator
    : GTE
    | GT
    | LTE
    | LT
    | EQ
    ;

number
    : DECIMAL
    ;

labelValue
    : STRING
    | IDENTIFIER
    ;

FIND: F I N D;
COUNT: C O U N T;
ME: M E;
WASTE: W A S T E;
WHERE: W H E R E;
AND: A N D;
CONFIDENCE: C O N F I D E N C E;
LABEL: L A B E L;
ORGANIC: O R G A N I C;
RECYCLABLE: R E C Y C L A B L E;
INORGANIC: I N O R G A N I C;

GTE: '>=';
GT: '>';
LTE: '<=';
LT: '<';
EQ: '==';
ASSIGN: '=';

DECIMAL
    : DIGIT+ ('.' DIGIT+)?
    ;

STRING
    : '"' (~["\\\r\n] | '\\' .)* '"'
    ;

IDENTIFIER
    : LETTER (LETTER | DIGIT | '_' | '-')*
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

fragment DIGIT: [0-9];
fragment LETTER: [a-zA-Z];
fragment A: [aA];
fragment B: [bB];
fragment C: [cC];
fragment D: [dD];
fragment E: [eE];
fragment F: [fF];
fragment G: [gG];
fragment H: [hH];
fragment I: [iI];
fragment J: [jJ];
fragment K: [kK];
fragment L: [lL];
fragment M: [mM];
fragment N: [nN];
fragment O: [oO];
fragment P: [pP];
fragment Q: [qQ];
fragment R: [rR];
fragment S: [sS];
fragment T: [tT];
fragment U: [uU];
fragment V: [vV];
fragment W: [wW];
fragment X: [xX];
fragment Y: [yY];
fragment Z: [zZ];
