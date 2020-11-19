from collections import namedtuple
from typing import Tuple, Callable, List

acc = namedtuple('acceleration', ['x', 'y'])


class Interaction:
    def __init__(self, obj1, obj2, law: Callable, params: List[str]):
        self.obj1 = obj1
        self.obj2 = obj2
        self.law = law
        self.params = params

    def calculate(self):
        p = ...
        return self.law, ...


class Physical:
    mass: float
    acc: Tuple[float, float]
    pass
