# parser combinator library Lippy.
"""
Lippy is a parser combinator library for Python 3.9+.
it's intentions are to help me parse out a custom programing language, but is a useful tool on its own.
Once complete will have a fully functional, declarative approach to parsing,
hopefully in a way that resembles the grammars themselves, so its super simple to use.
"""
from collections import namedtuple
from pprint import pprint
from components import *

Token = namedtuple("Token", ["type", "value"])

args = Text("a, b, c, d=1, e='2', f=TRUE")

VALUE = REGEX(r"[^,]+") | IDENTIFIER

argument_parser_pipe = Optional(
    Optional(
        IDENTIFIER
        & ASSIGN
        & VALUE
        & Many(
            Optional(WHITESPACE) & COMMA & IDENTIFIER & ASSIGN & VALUE
        )
    )
    & Optional(VALUE & Many(Optional(WHITESPACE) & COMMA & VALUE))
)


transform_args_to_tok = Parser(
    lambda parser_state: ParserState(
        parser_state.input,
        parser_state.pos,
        [
            Token(
                    "arg" if (s:=len(res.strip())) == 1 else "Kwarg", res.strip() if s == 1 else res.strip().split("="))
            for res in parser_state.result
            if res != ","
        ],
        parser_state.error_message,
        parser_state.error_state,
    )
)


res = args >> argument_parser_pipe >> transform_args_to_tok
pprint(res.value.result)
