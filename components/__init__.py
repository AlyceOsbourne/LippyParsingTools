from . import base, data_base
from .parser_base import *

Program = lambda to_parse: data_base.Monad >> to_parse >> ParserState


def parse_program(string, *parsers):
    prog = Program(string)
    for p in parsers:
        prog = prog >> p
    return prog


__all__ = "base", "data_base", "parser_base", "Program", "parse_program" + parser_base.__all__
