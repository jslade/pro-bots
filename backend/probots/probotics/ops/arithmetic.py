from .base import BinaryOperator
from .primitive import Primitive


class Addition(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value + right.value
        return Primitive.of(result)


class Subtraction(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value - right.value
        return Primitive.of(result)


class Multiplication(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value * right.value
        return Primitive.of(result)


class Division(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value / right.value
        return Primitive.of(result)
