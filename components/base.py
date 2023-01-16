class Meta(type):
    def __rshift__(self, other):
        return self(other)


class Pipeline(metaclass = Meta):
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        raise NotImplementedError

    def __str__(self):
        return f"{self.value}"

    def __rshift__(self, other):
        return self.__call__(other)


__all__ = "Pipeline", "Meta"