from functools import reduce


class Meta(type):
    def __rshift__(self, other):
        return self(other)


class Pipeline(metaclass=Meta):
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        raise NotImplementedError

    def __str__(self):
        return f"{self.value}"

    def __rshift__(self, other):
        return self.__call__(other)


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


__all__ = "Pipeline", "Meta", "Monad", "Functor"
