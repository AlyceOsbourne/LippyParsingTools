import re
from functools import cache

from .base import Meta, Pipeline


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


class Parser(Pipeline):
    def __str__(self):
        return f"Parser({self.value})"

    def __call__(self, state: ParserState) -> ParserState:
        return self.value(state)

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return Sequence(self, other)

    def __mul__(self, other):
        return Many(other)

    def __floordiv__(self, other):
        return Optional(other)

    def __neg__(self):
        return Not(self)

    def __invert__(self):
        return Optional(self)


class Sequence(Parser):
    def __init__(self, *parsers):
        super().__init__(parsers)

    def __call__(self, state: ParserState) -> ParserState:
        for p in self.value:
            state = p(state)
            if state.error_state:
                return state
        return state


class Or(Parser):
    # is supplied by Parser.__or__
    def __init__(self, *parsers):
        super().__init__(parsers)

    def __call__(self, state: ParserState) -> ParserState:
        while True:
            for p in self.value:
                s = p(state)
                if not s.error_state:
                    return s
            return state


class Many(Parser):

    def __call__(self, state: ParserState) -> ParserState:
        while not state.error_state:
            state = self.value(state)
        return state


class AtLeastOne(Many):

    def __call__(self, state: ParserState) -> ParserState:
        state = self.value(state)
        return super().__call__(state)


class Optional(Parser):

    def __call__(self, state: ParserState) -> ParserState:
        state = self.value(state)
        if state.error_state:
            return ParserState(state.input, state.pos, state.result, None, False)
        return state


class Not(Parser):

    def __call__(self, state: ParserState) -> ParserState:
        state = self.value(state)
        if state.error_state:
            return ParserState(state.input, state.pos, state.result, None, False)
        return state.error("not")


class And(Parser):

    def __call__(self, state: ParserState) -> ParserState:
        state = self.value(state)
        if state.error_state:
            return state
        return ParserState(state.input, state.pos, state.result, None, False)


class Regex(Parser):

    def __call__(self, state: ParserState) -> ParserState:
        match = self.value(state)
        if match.error_state:
            return match
        pattern = match.result
        match = re.match(pattern, state.input[match.pos:])
        if match:
            return state.append_and_shift(match.group(), len(match.group()))
        else:
            return state.error(f"Expected regex pattern {pattern}")


__all__ = (
        "ParserException",
        "ParserState",
        "Parser",
        "Sequence",
        "Or",
        "Many",
        "AtLeastOne",
        "Optional",
        "Not",
        "And",
)
