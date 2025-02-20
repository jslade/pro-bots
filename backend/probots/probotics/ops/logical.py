from .base import BinaryOperator, Operation
from .primitive import Primitive
from .stack_frame import StackFrame


class LogicalAnd(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = bool(left.value) and bool(right.value)
        return Primitive.of(result)


class LogicalOr(BinaryOperator):
    def _execute(self, left: Primitive, right: Primitive) -> Primitive:
        result = bool(left.value) or bool(right.value)
        return Primitive.of(result)


class LogicalNot(Operation):
    def execute(self, frame: StackFrame) -> None:
        right = frame.pop()
        result = not bool(right.value)
        frame.push(Primitive.of(result))
