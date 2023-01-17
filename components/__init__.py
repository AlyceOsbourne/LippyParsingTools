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


def CHAR(char):
    def _is_char(state: ParserState):
        # in range
        if state.pos < len(state.input):
            if state.is_(lambda x: x == char):
                return state.append(char).shift(1)
            return state.error(f"Expected {char} but got {state.input[state.pos]}")
        return state.error(f"Expected {char} but got EOF")

    return Parser(_is_char)


def CHARS(*chars):
    def _is_choice_chars(state: ParserState):
        if state.is_(lambda x: x in chars):
            return state.append(state.input[state.pos]).shift(1)
        return state.error(f"Expected one of {chars} but got {state.input[state.pos]}")

    return Parser(_is_choice_chars)


def WORD(word):
    def _is_word(state: ParserState):
        if state.pos + len(word) <= len(state.input):
            if state.input[state.pos: state.pos + len(word)] == word:
                return state.append(word).shift(len(word))
            return state.error(f"Expected {word} but got {state.input[state.pos]}")
        return state.error(f"Expected {word} but got EOF")

    return Parser(_is_word)


def WORDS(*words):
    def _is_choice_words(state: ParserState):
        for word in words:
            if state.input[state.pos: state.pos + len(word)] == word:
                return state.append(word).shift(len(word))
        return state.error(f"Expected one of {words} but got {state.input[state.pos]}")

    return Parser(_is_choice_words)


def REGEX(regex_pattern_str):
    def _is_regex(state: ParserState):
        if state.pos < len(state.input):
            match = re.match(regex_pattern_str, state.input[state.pos:])
            if match:
                return state.append(match.group(0)).shift(len(match.group(0)))
            return state.error(f"Expected {regex_pattern_str} but got {state.input[state.pos]}")
        return state.error(f"Expected {regex_pattern_str} but got EOF")

    return Parser(_is_regex)


@Parser
def ANY_CHAR(state: ParserState):
    if not state.is_eof():
        return state.append(state.input[state.pos]).shift(1)
    return state.error(f"Expected any char but got EOF")


@Parser
def ANY_WORD(state: ParserState):
    start = state.pos
    while not state.is_eof() and state.input[state.pos] not in " \t\r\n":
        state = state.shift(1)
    return state.append(state.input[start: state.pos])


@Parser
def EOF(state: ParserState):
    if state.pos < len(state.input):
        return state.error(f"Expected EOF but got {state.input[state.pos]}")
    return state


@Parser
def NUMBER(state: ParserState):
    # uses regex to parse a float or int
    if state.pos < len(state.input):
        match = re.match(r"(-?\d+(?:\.\d+)?)", state.input[state.pos:])
        if match:
            return state.append_and_shift(match.group(0), len(match.group(0)))
        return state.error(f"Expected number but got {state.input[state.pos]}")
    return state.error(f"Expected number but got EOF")


class SpecialWord(Enum):
    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = Parser(CHAR(value) if len(value) == 1 else WORD(value))
        return obj

    @classmethod
    def make_global(cls, name, **kwargs):
        # pylint: disable=unresolved-reference
        return global_enum(cls(name, kwargs))

    def __str__(self):
        return f"SpecialWord.{self.name}"

    def __call__(self, state: ParserState):
        return self.value(state)


Operators = SpecialWord.make_global(
        "Operators",
        ASSIGN = "=",
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

Brackets = SpecialWord.make_global(
        "Brackets",
        LPAREN = "(",
        RPAREN = ")",
        LBRACE = "{",
        RBRACE = "}",
        LBRACKET = "[",
        RBRACKET = "]",
)

Punctuation = SpecialWord.make_global(
        "Punctuation", COMMA = ",", COLON = ":", SEMICOLON = ";", DOT = "."
)

Other = SpecialWord.make_global(
        "Whitespace", NEWLINE = "\n", SPACE = " ", TAB = "\t", RETURN = "\r", WHITESPACE = " \t\r\n"
)


IDENTIFIER = REGEX(r"[a-zA-Z_][a-zA-Z0-9_]+")


__all__ = (
        "Text",
        "SpecialWord",
        "parse_text",
        "parse_file",
        "CHAR",
        "CHARS",
        "ANY_CHAR",
        "WORD",
        "WORDS",
        "ANY_WORD",
        "REGEX",
        "EOF",
        "NUMBER",
        "IDENTIFIER",
        *parser_base.__all__,
        *Operators.__members__.keys(),
        *Brackets.__members__.keys(),
        *Punctuation.__members__.keys(),
        *Other.__members__.keys(),
)
