from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .primitive import Primitive, PrimitiveType
    from .stack_frame import StackFrame


class Breakpoint(Exception):
    """Exception to be raised when a breakpoint is hit during execution.
    This allows the context to stop and let other contexts run.
    """

    def __init__(self, message: str, frame: "StackFrame") -> None:
        super().__init__(message)
        self.message = message
        self.frame = frame


class Operation:
    """Base class for an operation that can be executed"""

    def expected_args(self) -> list[tuple[str, list["PrimitiveType"]]]:
        return []

    def execute(self, frame: "StackFrame") -> "Primitive":
        raise NotImplementedError


class Immediate(Operation):
    """A terminal value in the parse tree that has an immediate value"""

    def __init__(self, value: "Primitive") -> None:
        self.value = value

    def execute(self, frame: "StackFrame") -> None:
        frame.push(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Immediate):
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

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other)

    def __repr__(self):
        return f"BinOp:{type(self).__name__}"
