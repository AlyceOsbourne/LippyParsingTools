# parser combinator library Lippy.
"""
Lippy is a parser combinator library for Python 3.9+.
it's intentions are to help me parse out a custom programing language, but is a useful tool on its own.
Once complete will have a fully functional, declarative approach to parsing,
hopefully in a way that resembles the grammars themselves, so its super simple to use.
"""
from enum import Enum, global_enum

import components
from components import *


@Parser
def is_eof(state: ParserState):
    if state.pos < len(state.input):
        return state.error(f"Expected EOF but got {state.input[state.pos]}")
    return state


@Parser
def is_space(state: ParserState):
    if state.is_(lambda x: x in ' \t\r\n'):
        return state.shift(1)
    return state.error(f"Expected space but got {state.input[state.pos]}")


@Parser
def is_number(state: ParserState):
    if state.is_(lambda x: x in '0123456789'):
        return state.append(state.input[state.pos]).shift(1)
    return state.error(f"Expected number but got {state.input[state.pos]}")


def is_char(char):
    def _is_char(state: ParserState):
        if state.is_(lambda x: x == char):
            return state.append(char).shift(1)
        return state.error(f"Expected {char} but got {state.input[state.pos]}")

    return Parser(_is_char)


def is_word(word):
    def _is_word(state: ParserState):
        if state[state.pos:state.pos + len(word)] == word:
            return state.append(word).shift(len(word))
        return state.error(f"Expected {word} but got {state.input[state.pos]}")

    return Parser(_is_word)


class Special(Enum):
    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = Parser(is_char(value) if len(value) == 1 else is_word(value))
        return obj

    @classmethod
    def make_global(cls, name, **kwargs):
        return global_enum(cls(name, kwargs))

    def __str__(self):
        return f"Special.{self.name}"

    def __call__(self, state: ParserState):
        return self.value(state)


Special.make_global("Operators",
                    ADD = "+", SUB = "-", MUL = "*",
                    DIV = "/", MOD = "%", POW = "^",
                    EQ = "==", NEQ = "!=", LT = "<",
                    GT = ">", LTE = "<=", GTE = ">="
                    )

Special.make_global("Brackets",
                    LPAREN = "(", RPAREN = ")",
                    LBRACE = "{", RBRACE = "}",
                    LBRACKET = "[", RBRACKET = "]"
                    )

Special.make_global("Punctuation", COMMA = ",", COLON = ":", SEMICOLON = ";", DOT = ".")
Special.make_global("Special", NEWLINE = "\n", SPACE = " ", TAB = "\t", RETURN = "\r")

if __name__ == '__main__':
    text = Text("""
    1 + 2 * 3;
    (1 + 2) * 3;
    1 + (2 * 3);""")

    # we need t parse expression, we can call the members of the Special enums from the global namespace to make life asier
