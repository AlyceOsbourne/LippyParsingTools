
from components import pipeline_meta
from components.parsers import *
from components.std import *



# Comments
LineComment = Terminal(r"//.*", "line_comment")
BlockComment = Terminal(r"/\*.*\*/", "block_comment")
Comment = (LineComment | BlockComment) + Tokenize("comment")

BinOp = Literal + ~Whitespace + BinaryOperators + ~Whitespace + Literal
BinOp = BinOp | (LParen + BinOp + RParen)
UnaryOp = UnaryOperators + ~Whitespace + BinOp
UnaryOp = UnaryOp | (LParen + UnaryOp + RParen)
Expr = BinOp | UnaryOp
Expr = Expr | (LParen + Expr + RParen)
Expr = (Expr | Literal | Identifier) + Tokenize("expr")

# Containers
CommeSeparatedExpr = Expr + +(Comma + Expr)
CommaSeperateKeyExprPairs = (Identifier + Colon + Expr) + +(
    Comma + Identifier + Colon + Expr
)
List = LBracket + ~CommeSeparatedExpr + RBracket
Tuple = LParen + ~CommeSeparatedExpr + RParen
Set = LBrace + ~CommeSeparatedExpr + RBrace
Dict = LBrace + ~CommaSeperateKeyExprPairs + RBrace
Container = (List | Tuple | Set | Dict) + Tokenize("container")

# Parameters
Arg = Identifier + ~(Colon + (Type | Identifier))
Kwarg = Arg + Equals + Expr
Args = Arg + +(Comma + Arg)
Kwargs = Kwarg + +(Comma + Kwarg)
Parameters = ~Args + ~Kwargs
Arguments = ~CommeSeparatedExpr + ~Kwargs

# Keywords


# Literals
Literal = (
    Number
    | String
    | Boolean
    | List
    | Tuple
    | Set
    | Dict
    | Identifier
) + Tokenize("literal")

