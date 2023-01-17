from enum import Enum, global_enum

from . import base, data_base
from .parser_base import *
import re

Text = lambda to_parse: data_base.Monad >> to_parse >> ParserState


def parse_text(string, *parsers):
    prog = Text(string)
    for p in parsers:
        prog = prog >> p
    return prog


def parse_file(file, *parsers):
    with open(file, "r") as f:
        return parse_text(f.read(), *parsers)


def is_char(char):
    def _is_char(state: ParserState):
        # in range
        if state.pos < len(state.input):
            if state.is_(lambda x: x == char):
                return state.append(char).shift(1)
            return state.error(f"Expected {char} but got {state.input[state.pos]}")
        return state.error(f"Expected {char} but got EOF")

    return Parser(_is_char)


def is_chars(*chars):
    def _is_choice_chars(state: ParserState):
        if state.is_(lambda x: x in chars):
            return state.append(state.input[state.pos]).shift(1)
        return state.error(f"Expected one of {chars} but got {state.input[state.pos]}")

    return Parser(_is_choice_chars)


def is_word(word):
    def _is_word(state: ParserState):
        if state.pos + len(word) <= len(state.input):
            if state.input[state.pos: state.pos + len(word)] == word:
                return state.append(word).shift(len(word))
            return state.error(f"Expected {word} but got {state.input[state.pos]}")
        return state.error(f"Expected {word} but got EOF")

    return Parser(_is_word)


def is_words(*words):
    def _is_choice_words(state: ParserState):
        for word in words:
            if state.input[state.pos: state.pos + len(word)] == word:
                return state.append(word).shift(len(word))
        return state.error(f"Expected one of {words} but got {state.input[state.pos]}")

    return Parser(_is_choice_words)


def is_regex(regex_pattern_str):
    def _is_regex(state: ParserState):
        match = re.match(regex_pattern_str, state.input[state.pos:])
        if match:
            return state.append(match.group(0)).shift(len(match.group(0)))
        return state.error(f"Expected {regex_pattern_str} but got {state.input[state.pos]}")

    return Parser(_is_regex)


@Parser
def is_any_char(state: ParserState):
    if not state.is_eof():
        return state.append(state.input[state.pos]).shift(1)
    return state.error(f"Expected any char but got EOF")


@Parser
def is_any_word(state: ParserState):
    start = state.pos
    while not state.is_eof() and state.input[state.pos] not in " \t\r\n":
        state = state.shift(1)
    return state.append(state.input[start: state.pos])


@Parser
def is_whitespace(state: ParserState):
    if state.pos < len(state.input):
        if state.is_(str.isspace):
            return state.append(state.input[state.pos]).shift(1)
        return state.error(f"Expected whitespace but got {state.input[state.pos]}")
    return state.error(f"Expected whitespace but got EOF")


@Parser
def is_eof(state: ParserState):
    if state.pos < len(state.input):
        return state.error(f"Expected EOF but got {state.input[state.pos]}")
    return state


@Parser
def is_number(state: ParserState):
    if state.is_(lambda x: x in "0123456789"):
        return state.append(state.input[state.pos]).shift(1)
    return state.error(f"Expected number but got {state.input[state.pos]}")


class Special(Enum):
    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = Parser(is_char(value) if len(value) == 1 else is_word(value))
        return obj

    @classmethod
    def make_global(cls, name, **kwargs):
        # pylint: disable=unresolved-reference
        return global_enum(cls(name, kwargs))

    def __str__(self):
        return f"Special.{self.name}"

    def __call__(self, state: ParserState):
        return self.value(state)


Operators = Special.make_global(
        "Operators",
        ADD = "+",
        SUB = "-",
        MUL = "*",
        DIV = "/",
        MOD = "%",
        POW = "^",
        EQ = "==",
        NEQ = "!=",
        LT = "<",
        GT = ">",
        LTE = "<=",
        GTE = ">=",
)

Brackets = Special.make_global(
        "Brackets",
        LPAREN = "(",
        RPAREN = ")",
        LBRACE = "{",
        RBRACE = "}",
        LBRACKET = "[",
        RBRACKET = "]",
)

Punctuation = Special.make_global(
        "Punctuation", COMMA = ",", COLON = ":", SEMICOLON = ";", DOT = "."
)
Whitespace = Special.make_global(
        "Whitespace", NEWLINE = "\n", SPACE = " ", TAB = "\t", RETURN = "\r"
)

__all__ = (
        "Text",
        "Special",
        "parse_text",
        "parse_file",
        "is_char",
        "is_chars",
        "is_any_char",
        "is_word",
        "is_words",
        "is_any_word",
        "is_regex",
        "is_eof",
        "is_number",
        "is_whitespace",
        *parser_base.__all__,
        *Operators.__members__.keys(),
        *Brackets.__members__.keys(),
        *Punctuation.__members__.keys(),
        *Whitespace.__members__.keys(),
)
