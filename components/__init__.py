from collections import namedtuple

from components import pipeline_meta
from components.parsers import *

Text = lambda to_parse: pipeline_meta.Monad >> to_parse >> ParserState
Token = namedtuple("Token", ["type", "value"])


def parse_text(string, *parsers):
    prog = Text(string)
    for p in parsers:
        prog = prog >> p
    return prog


def parse_file(file, *parsers):
    with open(file, "r") as f:
        return parse_text(f.read(), *parsers)


@Parser
def EOF(state: ParserState):
    if state.pos < len(state.input):
        return state.error(f"Expected EOF but got {state.input[state.pos]}")
    return state


@Parser
def EOL(state: ParserState):
    if state.pos < len(state.input) and state.input[state.pos] != "\n":
        return state.error(f"Expected EOL but got {state.input[state.pos]}")
    return state


@Parser
def Whitespace(state: ParserState):
    if state.pos < len(state.input) and state.input[state.pos] in " \t":
        return state.shift(1)
    return state


def Terminal(pattern, token_type=None):
    def regex(state: ParserState):
        match = re.match(pattern, state.input[state.pos :], re.MULTILINE)
        if match:
            if token_type:
                return state.append_and_shift(
                    Token(token_type, match.group()), len(match.group())
                )
            return state.append_and_shift(match.group(), len(match.group()))
        else:
            return state.error(f"Expected regex pattern {pattern}")

    return Parser(regex)


Regex = Terminal

Identifier = Terminal(r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier")
Integer = Terminal(r"[0-9]+", "integer")
Float = Terminal(r"[0-9]+\.[0-9]+", "float")
Binary = Terminal(r"0b[01]+", "binary")
Octal = Terminal(r"0o[0-7]+", "octal")
Hex = Terminal(r"0x[0-9a-fA-F]+", "hex")
Expontential = Terminal(r"[0-9]+e[0-9]+", "exponential")
Number = Integer | Float | Binary | Octal | Hex | Expontential
String = Terminal(r'"[^"]*"', "string")
Boolean = Terminal(r"true|false", "boolean")
Literal = Number | String | Boolean

# brackets
LParen = Terminal(r"\(", "lparen")
RParen = Terminal(r"\)", "rparen")
LBracket = Terminal(r"\[", "lbracket")
RBracket = Terminal(r"\]", "rbracket")
LBrace = Terminal(r"\{", "lbrace")
RBrace = Terminal(r"\}", "rbrace")

# operators
Plus = Terminal(r"\+", "plus")
Minus = Terminal(r"-", "minus")
Multiply = Terminal(r"\*", "multiply")
Divide = Terminal(r"/", "divide")
Modulo = Terminal(r"%", "modulo")
Exponent = Terminal(r"\*\*", "exponent")
Equals = Terminal(r"=", "equals")
NotEquals = Terminal(r"!=", "not_equals")
LessThan = Terminal(r"<", "less_than")
GreaterThan = Terminal(r">", "greater_than")
LessThanEquals = Terminal(r"<=", "less_than_equals")
GreaterThanEquals = Terminal(r">=", "greater_than_equals")
And = Terminal(r"&&", "and")
Or = Terminal(r"\|\|", "or")
Not = Terminal(r"!", "not")
Dot = Terminal(r"\.", "dot")
Comma = Terminal(r",", "comma")
Semicolon = Terminal(r";", "semicolon")
Colon = Terminal(r":", "colon")
Arrow = Terminal(r"->", "arrow")
At = Terminal(r"@", "at")
Hash = Terminal(r"#", "hash")
Dollar = Terminal(r"\$", "dollar")
Ampersand = Terminal(r"&", "ampersand")
Pipe = Terminal(r"\|", "pipe")
Tilde = Terminal(r"~", "tilde")
Caret = Terminal(r"\^", "caret")
Backtick = Terminal(r"`", "backtick")
QuestionMark = Terminal(r"\?", "question_mark")
Underscore = Terminal(r"_", "underscore")
Backslash = Terminal(r"\\", "backslash")
Slash = Terminal(r"/", "slash")
SingleQuote = Terminal(r"'", "single_quote")
DoubleQuote = Terminal(r'"', "double_quote")
Assign = Terminal(r":=", "assign")
PlusEquals = Terminal(r"\+=", "plus_equals")
MinusEquals = Terminal(r"-=", "minus_equals")
MultiplyEquals = Terminal(r"\*=", "multiply_equals")
DivideEquals = Terminal(r"/=", "divide_equals")
ModuloEquals = Terminal(r"%=", "modulo_equals")
ExponentEquals = Terminal(r"\*\*=", "exponent_equals")
AndEquals = Terminal(r"&=", "and_equals")
OrEquals = Terminal(r"\|=", "or_equals")
XorEquals = Terminal(r"\^=", "xor_equals")
ShiftLeft = Terminal(r"<<", "shift_left")
ShiftRight = Terminal(r">>", "shift_right")
ShiftLeftEquals = Terminal(r"<<=", "shift_left_equals")
ShiftRightEquals = Terminal(r">>=", "shift_right_equals")

UnaryOperators = Not | Plus | Minus | Tilde
BinaryOperators = (
    Plus
    | Minus
    | Multiply
    | Divide
    | Modulo
    | Exponent
    | Equals
    | NotEquals
    | LessThan
    | GreaterThan
    | LessThanEquals
    | GreaterThanEquals
    | And
    | Or
    | Dot
    | Comma
    | Semicolon
    | Colon
    | Arrow
    | At
    | Hash
    | Dollar
    | Ampersand
    | Pipe
    | Tilde
    | Caret
    | Backtick
    | QuestionMark
    | Underscore
    | Backslash
    | Slash
    | SingleQuote
    | DoubleQuote
    | Assign
    | PlusEquals
    | MinusEquals
    | MultiplyEquals
    | DivideEquals
    | ModuloEquals
    | ExponentEquals
    | AndEquals
    | OrEquals
    | XorEquals
    | ShiftLeft
    | ShiftRight
    | ShiftLeftEquals
    | ShiftRightEquals
)

BinOp = Literal + ~Whitespace + BinaryOperators + ~Whitespace + Literal
BinOp = BinOp | (LParen + BinOp + RParen)
UnaryOp = UnaryOperators + ~Whitespace + BinOp
UnaryOp = UnaryOp | (LParen + UnaryOp + RParen)
Expr = BinOp | UnaryOp
Expr = Expr | (LParen + Expr + RParen)
Expr = Expr | Literal | Identifier

# Flow control
If = Terminal(r"if", "if")
Else = Terminal(r"else", "else")
For = Terminal(r"for", "for")
While = Terminal(r"while", "while")
Do = Terminal(r"do", "do")
In = Terminal(r"in", "in")
Return = Terminal(r"return", "return")
Break = Terminal(r"break", "break")
Continue = Terminal(r"continue", "continue")

# Types
Int = Terminal(r"int", "int")
Float = Terminal(r"float", "float")
String = Terminal(r"string", "string")
Boolean = Terminal(r"boolean", "boolean")
Void = Terminal(r"void", "void")
Type = Int | Float | String | Boolean | Void


# Comments
LineComment = Terminal(r"//.*", "line_comment")
BlockComment = Terminal(r"/\*.*\*/", "block_comment")
Comment = LineComment | BlockComment

# Containers
CommeSeparatedExpr = Expr + +(Comma + Expr)
CommaSeperateKeyExprPairs = (Identifier + Colon + Expr) + +(
    Comma + Identifier + Colon + Expr
)
List = LBracket + ~CommeSeparatedExpr + RBracket
Tuple = LParen + ~CommeSeparatedExpr + RParen
Set = LBrace + ~CommeSeparatedExpr + RBrace
Dict = LBrace + ~CommaSeperateKeyExprPairs + RBrace
Container = List | Tuple | Set | Dict

# Parameters
Arg = Identifier + ~(Colon + (Type | Identifier))
Kwarg = Arg + Equals + Expr
Args = Arg + +(Comma + Arg)
Kwargs = Kwarg + +(Comma + Kwarg)
Parameters = ~Args + ~Kwargs
Arguments = ~CommeSeparatedExpr + ~Kwargs

# Keywords
Keyword = (
    If
    | Else
    | For
    | While
    | Do
    | In
    | Return
    | Break
    | Continue
    | Int
    | Float
    | String
    | Boolean
    | Void
)

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
)

