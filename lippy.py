# parser combinator library Lippy.
"""
Lippy is a parser combinator library for Python 3.9+.
it's intentions are to help me parse out a custom programing language, but is a useful tool on its own.
Once complete will have a fully functional, declarative approach to parsing,
hopefully in a way that resembles the grammars themselves, so its super simple to use.
"""
import components
__all__ = ("components",)

from components import *

if __name__ == '__main__':
    import functools
    to_parse = Text("abc")


    def _parse_single_char(char):
        def _parse_char(state: ParserState):
            if state.input[state.pos] == char:
                return ParserState(state.input, state.pos + 1, state.result + char, None, False)
            return ParserState(state.input, state.pos, state.result, f"Expected {char} but got {state.input[state.pos]}", True)
        return Parser(_parse_char)


    parse_a = Parser(_parse_single_char("a"))
    parse_b = Parser(_parse_single_char("b"))
    parse_c = Parser(_parse_single_char("c"))

    parse_a_or_b = parse_a | parse_b
    parse_a_and_b = parse_a & parse_b
    parse_a_and_b_and_c = parse_a_and_b & parse_c

    to_parse >> parse_a_or_b >> print
    to_parse >> parse_a_and_b >> print
    to_parse >> parse_a_and_b_and_c >> print

