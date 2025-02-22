from typing import Callable, Optional, TypeAlias

from .base import Operation
from .primitive import Primitive
from .stack_frame import StackFrame

NativeFunc: TypeAlias = Callable[[StackFrame], Optional[Primitive]]


class Native(Operation):
    """An operation that is implemented natively in python."""

    def __init__(self, func: NativeFunc) -> None:
        self.func = func

    def execute(self, frame: StackFrame) -> None:
        """The result of the function is passed as the return value for the frame"""
        result = self.func(frame)
        if result is not None:
            frame.push(result)

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.func == other.func

    def __repr__(self) -> str:
        return f"Native({self.func.__name__})"
