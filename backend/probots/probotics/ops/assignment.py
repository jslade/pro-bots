from typing import Optional
from .base import Operation
from .primitive import Primitive
from .stack_frame import StackFrame


class Assignment(Operation):
    """Assignment operator for assigning values to variables. The variable can
    be a symbol or a property of an object.
    """

    def execute(self, frame: StackFrame) -> None:
        value = frame.pop()
        target = frame.pop()
        result = self.assign(target, value, frame)
        if result is not None:
            frame.push(result)

    def assign(
        self, left: Primitive, right: Primitive, frame: StackFrame
    ) -> Optional[Primitive]:
        if left.is_symbol:
            frame.set(left.value, right)

        elif left.is_property:
            target, name = left.value
            if type(target) is list:
                while len(target) <= name:
                    target.append(None)
            target[name] = right
        else:
            raise ValueError(f"Invalid assignment target: {left.value} {left.type.value}")

        # Assignment yields the value of the right side, unless it's a callable.
        # This is mostly just to keep the noise down in the terminal.
        if right.is_block:
            return None
        return right
