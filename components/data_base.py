from functools import reduce

from base import Pipeline


class Monad(Pipeline):
    """We use this to contain the data that we are parsing"""

    def __call__(self, f) -> "Monad":
        return Monad(f(self.value))


class Functor(Pipeline):
    def __call__(self, f) -> Monad:
        # self.value can be an iter or a single function
        if callable(self.value):
            return Monad(self.value(f))
        return Monad(reduce(lambda x, y: y(x), self.value, f))


__all__ = "Monad", "Functor"