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

    def _parse_single_char(char):
        def _parse_char(state: ParserState):
            # if in range
            if state.pos < len(state.input):
                if state.input[state.pos] == char:
                    return state.append(char).shift(1)
                return state.error(f"Expected {char} but got {state.input[state.pos]}")
            return state.error(f"Expected {char} but got EOF")

        return _parse_char


    def _parse_single_word(word):
        def _parse_word(state: ParserState):
            if state.pos + len(word) <= len(state.input):
                if state.input[state.pos:state.pos + len(word)] == word:
                    return state.append(word).shift(len(word))
                return state.error(f"Expected {word} but got {state.input[state.pos:state.pos + len(word)]}")
            return state.error(f"Expected {word} but got EOF")

        return _parse_word


    parse_a = Parser(_parse_single_char("a"))
    parse_b = Parser(_parse_single_char("b"))
    parse_c = Parser(_parse_single_char("c"))
    parse_abc = Parser(_parse_single_word("abc"))

    parse_a_or_b = parse_a | parse_b
    parse_a_and_b = parse_a & parse_b
    parse_a_and_b_and_c = parse_a_and_b & parse_c

    Text("b") >> parse_a_or_b >> print
    Text("ab") >> parse_a_and_b >> print
    Text("abc") >> parse_a_and_b_and_c >> print
    Text("abc") >> parse_abc >> print


