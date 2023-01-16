from . import base, data_base
from .parser_base import *
Text = lambda to_parse: data_base.Monad >> to_parse >> ParserState


def parse_text(string, *parsers):
    prog = Text(string)
    for p in parsers:
        prog = prog >> p
    return prog


__all__ = ("base", "data_base", "parser_base", "Text", "parse_text") + parser_base.__all__

