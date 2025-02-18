from typing import Callable, TypeAlias

from .base import Operation
from .primitive import Primitive
from .stack_frame import StackFrame

NativeFunc: TypeAlias = Callable[[StackFrame], Primitive]


class Native(Operation):
    """An operation that is implemented natively in python."""

    def __init__(self, func: NativeFunc) -> None:
        self.func = func

    def execute(self, frame: StackFrame) -> None:
        """The result of the function is passed as the return value for the frame"""
        result = self.func(frame)
        frame.push(result)
