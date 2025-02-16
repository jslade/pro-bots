from .base import Operation
from .primitive import Primitive
from .stack_frame import StackFrame, UndefinedSymbol


class ValueOf(Operation):
    """Return the value of a symbol in the current scope."""

    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, frame: "StackFrame") -> None:
        try:
            value = frame.get(self.name)
        except UndefinedSymbol:
            value = Primitive.of(None)
        frame.push(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueOf):
            return False
        return self.name == other.name

    def __repr__(self):
        return "ValueOf(" + self.name + ")"
