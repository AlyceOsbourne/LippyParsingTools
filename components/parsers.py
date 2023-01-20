import re
from functools import cache

from .pipeline_meta import Meta, Pipeline


class ParserException(Exception):
    pass


class ParserState(metaclass = Meta):
    """This contains the state of the parser"""

    def __init__(
            self,
            to_parse: str,
            pos: int = 0,
            result: list = None,
            error_message: str = None,
            error_state: bool = False,
    ):
        self.input = to_parse
        self.pos = pos
        self.result = result or []
        self.error_message = error_message
        self.error_state = error_state

    def is_eof(self):
        return self.pos >= len(self.input) or self.input[self.pos] is None

    def map(self, f):
        return ParserState(
                self.input, self.pos, f(self.result), self.error_message, self.error_state
        )

    def is_(self, f):
        if not callable(f):
            raise ValueError("f is not a callable")
        if self.input is None:
            raise ValueError("input is None")
        if self.pos >= len(self.input) or self.input[self.pos] is None:
            return False
        return f(self.input[self.pos])

    def shift(self, i):
        if self.error_state:
            return self
        if i <= 0:
            raise ValueError("i must be > 0")
        if self.pos + i > len(self.input):
            return self.error("shift out of bounds")
        return ParserState(self.input, self.pos + i, self.result, None, False)

    def append(self, s):
        if self.error_state:
            return self
        try:
            return ParserState(
                    self.input,
                    self.pos,
                    self.result + [s],
                    self.error_message,
                    self.error_state,
            )
        except:
            return ParserState(
                    self.input, self.pos, self.result, self.error_message, True
            )

    def append_and_shift(self, s, i):
        return self.append(s).shift(i)

    def error(self, msg):
        return ParserState(self.input, self.pos, self.result, msg, True)

    def __repr__(self):
        return f"ParserState(input={self.input!r}, pos={self.pos!r}, result={self.result!r}, error={self.error_message!r}, is_error={self.error_state!r})"

    def __str__(self):
        return " ".join(map(str, self.result))


class Parser(Pipeline):
    def __str__(self):
        return f"Parser({self.value})"

    def __call__(self, state: ParserState) -> ParserState:
        return self.value(state)

    def __or__(self, *other):
        """This parser or that parser, if this parser fails, try that parser"""

        def parser(state: ParserState):
            result = self(state)
            if not result.error_state:
                return result
            for p in other:
                result = p(state)
                if not result.error_state:
                    return result
            return result.error(f"Expected {self} or {other}")

        return Parser(parser)

    def __add__(self, other):
        """This parser and that parser, if this parser fails, don't try that parser"""

        def parser(state: ParserState):
            result = self(state)
            if result.error_state:
                return result
            return other(result)

        return Parser(parser)

    def __pos__(self):
        """Many of this parser"""

        def parser(state: ParserState):
            result = self(state)
            if result.error_state:
                return result
            while not result.error_state:
                result = self(result)
            return result

        return Parser(parser)

    def __neg__(self):
        """Not this parser"""

        def parser(state: ParserState):
            result = self(state)
            if result.error_state:
                return state
            return result.error(f"Expected not {self}")

        return Parser(parser)

    def __invert__(self):
        """Optional this parser"""

        def parser(state: ParserState):
            result = self(state)
            if result.error_state:
                return state
            return result

        return Parser(parser)

    def __and__(self, other):
        """Sequence this parser and that parser"""

        def parser(state: ParserState):
            result = self(state)
            if result.error_state:
                return result
            return other(result)

        return Parser(parser)
