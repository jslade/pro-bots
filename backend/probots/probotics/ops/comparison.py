from .base import BinaryOperator

from .primitive import Primitive


class CompareEqual(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value == right.value
        return Primitive.of(result)


class CompareNotEqual(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value != right.value
        return Primitive.of(result)


class CompareLessThan(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value < right.value
        return Primitive.of(result)


class CompareLessThanOrEqual(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value <= right.value
        return Primitive.of(result)


class CompareGreaterThan(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value > right.value
        return Primitive.of(result)


class CompareGreaterThanOrEqual(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = left.value >= right.value
        return Primitive.of(result)
