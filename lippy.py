# parser combinator library Lippy.
"""
Lippy is a parser combinator library for Python 3.9+.
it's intentions are to help me parse out a custom programing language, but is a useful tool on its own.
Once complete will have a fully functional, declarative approach to parsing,
hopefully in a way that resembles the grammars themselves, so its super simple to use.
"""

from components import *

hello_world_pipe = is_words("Hello", "Goodbye") & Optional(is_whitespace) & is_word("World") & Optional(is_eof)

Text("Hello World") >> hello_world_pipe >> print
Text("Goodbye World") >> hello_world_pipe >> print
Text("Hello World!") >> hello_world_pipe >> print
Text("HelloWorld") >> hello_world_pipe >> print
