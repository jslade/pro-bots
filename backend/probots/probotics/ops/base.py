from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .primitive import Primitive
    from .stack_frame import StackFrame


class Operation:
    """Base class for an operation that can be executed"""

    def execute(self, frame: "StackFrame") -> None:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        return type(other) is type(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class Immediate(Operation):
    """A terminal value in the parse tree that has an immediate value"""

    def __init__(self, value: "Primitive") -> None:
        self.value = value

    def execute(self, frame: "StackFrame") -> None:
        frame.push(self.value)

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.value == other.value

    def __repr__(self):
        return "Immediate(" + repr(self.value) + ")"


class BinaryOperator(Operation):
    """Base class for binary operators (primarily arithmetic and logical)"""

    def execute(self, frame: "StackFrame") -> None:
        right = frame.pop()
        left = frame.pop()
        result = self._execute(left, right)
        frame.push(result)

    def _execute(self, left: "Primitive", right: "Primitive") -> "Primitive":
        raise NotImplementedError
