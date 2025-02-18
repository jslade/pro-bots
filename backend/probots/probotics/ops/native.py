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
        frame.push(Primitive.of(self.func(frame)))
