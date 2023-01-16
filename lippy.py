from components.data_base import Monad
from components.parser_base import ParserState, Parser
Program = lambda to_parse: Monad >> to_parse >> ParserState
