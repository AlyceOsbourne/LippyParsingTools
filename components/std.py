import re

from components import Parser, ParserState, pipeline_meta


def parse_text(string, *parsers):
    prog = Text(string)
    for p in parsers:
        prog = prog >> p
    return prog


def parse_file(file, *parsers):
    with open(file, "r") as f:
        return parse_text(f.read(), *parsers)


class Token:

    def __str__(self):
        return f"{self.type}({' '.join(map(str, self.value))})"

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r})"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value

    def __hash__(self):
        return hash((self.type, self.value))

    def __init__(self, _type, value = ""):
        self.type = _type
        self.value = value


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


def Regex(pattern):
    def regex(state: ParserState):
        match = re.match(pattern, state.input[state.pos:], re.MULTILINE)
        if match:
            return state.append_and_shift(match.group(), len(match.group()))
        else:
            return state.error(f"Expected regex pattern {pattern}")

    return Parser(regex)


# parser that makes the result a token of a specific type
def Tokenize(token_type):
    def tokenize(state: ParserState):
        # takes the result, and makes a token from it with the given type
        return ParserState(
                state.input,
                state.pos,
                [Token(token_type, state.result)],
                state.error_message,
                state.error_state,
        )

    return Parser(tokenize)


def Text(to_parse):
    return pipeline_meta.Monad >> to_parse >> ParserState


def Terminal(pattern, token_type):
    return Regex(pattern) + Tokenize(token_type)


# Literals
Identifier = Terminal(r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER")
Float = Terminal(r"[0-9]+\.[0-9]+", "FLOAT")
Integer = Terminal(r"[0-9]+", "INTEGER")
Number = (Float | Integer) + Tokenize("NUMBER")
String = Terminal(r'"[^"]*"|\'[^\']*\'', "STRING")
Boolean = Terminal(r"true|false", "BOOLEAN")
Literal = Number | String | Boolean | Identifier

# brackets
LParen = Terminal(r"\(", "LPAREN")
RParen = Terminal(r"\)", "RPAREN")
LBracket = Terminal(r"\[", "LBRACKET")
RBracket = Terminal(r"\]", "RBRACKET")
LBrace = Terminal(r"\{", "LBRACE")
RBrace = Terminal(r"\}", "RBRACE")

# operators
Plus = Terminal(r"\+", "PLUS")
Minus = Terminal(r"-", "MINUS")
Multiply = Terminal(r"\*", "MULTIPLY")
Divide = Terminal(r"/", "DIVIDE")
Modulo = Terminal(r"%", "MODULO")
Exponent = Terminal(r"\*\*", "EXPONENT")
Equals = Terminal(r"=", "EQUALS")
NotEquals = Terminal(r"!=", "NOT_EQUALS")
LessThan = Terminal(r"<", "LESS_THAN")
GreaterThan = Terminal(r">", "GREATER_THAN")
LessThanEquals = Terminal(r"<=", "LESS_THAN_EQUALS")
GreaterThanEquals = Terminal(r">=", "GREATER_THAN_EQUALS")
And = Terminal(r"&", "AND")
Or = Terminal(r"\|", "OR")
Not = Terminal(r"!", "NOT")
Dot = Terminal(r"\.", "DOT")
Comma = Terminal(r",", "COMMA")
Semicolon = Terminal(r";", "SEMICOLON")
Colon = Terminal(r":", "COLON")
Arrow = Terminal(r"->", "ARROW")
At = Terminal(r"@", "AT")
Hash = Terminal(r"#", "HASH")
Dollar = Terminal(r"\$", "DOLLAR")
Ampersand = Terminal(r"&", "AMPERSAND")
Tilde = Terminal(r"~", "TILDE")
Caret = Terminal(r"\^", "CARET")
Backtick = Terminal(r"`", "BACKTICK")
QuestionMark = Terminal(r"\?", "QUESTION_MARK")
Underscore = Terminal(r"_", "UNDERSCORE")
Backslash = Terminal(r"\\", "BACKSLASH")
Slash = Terminal(r"/", "SLASH")
SingleQuote = Terminal(r"'", "SINGLE_QUOTE")
DoubleQuote = Terminal(r'"', "DOUBLE_QUOTE")
Assign = Terminal(r"=", "ASSIGN")
PlusEquals = Terminal(r"\+=", "PLUS_EQUALS")
MinusEquals = Terminal(r"-=", "MINUS_EQUALS")
MultiplyEquals = Terminal(r"\*=", "MULTIPLY_EQUALS")
DivideEquals = Terminal(r"/=", "DIVIDE_EQUALS")
ModuloEquals = Terminal(r"%=", "MODULO_EQUALS")
ExponentEquals = Terminal(r"\*\*=", "EXPONENT_EQUALS")
AndEquals = Terminal(r"&=", "AND_EQUALS")
OrEquals = Terminal(r"\|=", "OR_EQUALS")
XorEquals = Terminal(r"\^=", "XOR_EQUALS")
ShiftLeft = Terminal(r"<<", "SHIFT_LEFT")
ShiftRight = Terminal(r">>", "SHIFT_RIGHT")
ShiftLeftEquals = Terminal(r"<<=", "SHIFT_LEFT_EQUALS")
ShiftRightEquals = Terminal(r">>=", "SHIFT_RIGHT_EQUALS")

Operator = (
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
                   | Not
                   | Dot
                   | Comma
                   | Semicolon
                   | Colon
                   | Arrow
                   | At
                   | Hash
                   | Dollar
                   | Ampersand
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
           ) + Tokenize("OPERATOR")

# Flow control
If = Terminal(r"if", "IF")
Else = Terminal(r"else", "ELSE")
For = Terminal(r"for", "FOR")
While = Terminal(r"while", "WHILE")
Do = Terminal(r"do", "DO")
In = Terminal(r"in", "IN")
Return = Terminal(r"return", "RETURN")
Break = Terminal(r"break", "BREAK")
Continue = Terminal(r"continue", "CONTINUE")

FlowControl = If | Else | For | While | Do | In | Return | Break | Continue

if __name__ == "__main__":
    # test literals
    Text("X") >> Literal >> print
    Text("123") >> Literal >> print
    Text("123.456") >> Literal >> print
    Text('"hello"') >> Literal >> print
    Text("true") >> Literal >> print
    Text("false") >> Literal >> print

    # test operators
    Text("+") >> Operator >> print
    Text("+=") >> Operator >> print
    Text("**=") >> Operator >> print
    Text(">>=") >> Operator >> print

    # test flow control
    Text("if") >> FlowControl >> print
    Text("else") >> FlowControl >> print
    Text("for") >> FlowControl >> print
    Text("while") >> FlowControl >> print
    Text("do") >> FlowControl >> print
    Text("in") >> FlowControl >> print
    Text("return") >> FlowControl >> print

    # test identifiers
    Text("x") >> Identifier >> print
    Text("x123") >> Identifier >> print
    Text("x_123") >> Identifier >> print
    Text("x_123_") >> Identifier >> print
    Text("x_123_abc") >> Identifier >> print

    # basic assignment statement
    Assignment = (
                         Identifier  # must start with an identifier
                         + ~Whitespace  # followed by optional whitespace
                         + Assign  # followed by an assignment operator
                         + ~Whitespace  # followed by optional whitespace
                         + Literal  # followed by a literal
                         + ~Whitespace  # followed by optional whitespace
                         + Semicolon  # followed by a semicolon
                 ) + Tokenize("ASSIGNMENT")  # and tokenized as an assignment statement

    Text("x = 123;") >> Assignment >> print
    # >> are pipelines, they push the value from this parser to the next, this works cause of monoids
