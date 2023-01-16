from components.base import Meta, Pipeline


class ParserState(metaclass = Meta):
    """This contains the state of the parser"""

    def __init__(self,
                 to_parse: str,
                 pos: int = 0,
                 result: str = "",
                 error_message: str = None,
                 error_state: bool = False):
        self.input = to_parse
        self.pos = pos
        self.result = result
        self.error_message = error_message
        self.error_state = error_state

    def __str__(self):
        return f"ParserState(input={self.input}, pos={self.pos}, result={self.result}, error={self.error_message}, is_error={self.error_state})"

    def is_eof(self):
        return self.pos >= len(self.input) or self.input[self.pos] is None

    def bind(self, f):
        return ParserState(self.input, self.pos, f(self.result), self.error_message, self.error_state)

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
            return ParserState(self.input, self.pos, self.result + s, self.error_message, self.error_state)
        except:
            return ParserState(self.input, self.pos, self.result, self.error_message, True)

    def error(self, msg):
        return ParserState(self.input, self.pos, self.result, msg, True)

    def bind_and_shift(self, f, i):
        return self.bind(f).shift(i)


class Parser(Pipeline):

    def __str__(self):
        return f"Parser({self.value})"

    def __call__(self, state: ParserState) -> ParserState:
        return self.value(state)
