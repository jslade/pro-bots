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
        frame.push(result)

    def assign(self, left: Primitive, right: Primitive, frame: StackFrame) -> Primitive:
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

        # Assignment always yields the value of the right side
        return right
