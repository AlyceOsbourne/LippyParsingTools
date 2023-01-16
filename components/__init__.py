from . import base, data_base
from .parser_base import *
Text = lambda to_parse: data_base.Monad >> to_parse >> ParserState


def parse_text(string, *parsers):
    prog = Text(string)
    for p in parsers:
        prog = prog >> p
    return prog


def parse_file(file, *parsers):
    with open(file, 'r') as f:
        return parse_text(f.read(), *parsers)



__all__ = ("base", "data_base", "parser_base", "Text", "parse_text") + parser_base.__all__

