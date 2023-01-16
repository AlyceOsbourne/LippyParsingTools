from components.data_base import Monad
from components.parser_base import ParserState

Program = lambda to_parse: Monad >> to_parse >> ParserState

__all__ = "Program",
