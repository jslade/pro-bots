from .base import Immediate, Operation
from .primitive import Primitive
from .stack_frame import StackFrame


class Property(Operation):
    """Make a reference to an object property. The target object is popped from the stack,
    while the name of the property is stored in the operation.
    """

    def __init__(self, name: str):
        self.name = name

    def execute(self, frame: "StackFrame") -> None:
        target = frame.pop()
        if not target.is_object:
            raise TypeError(f"Cannot get property of {target.type}")
        property = Primitive.property(target.value, self.name)
        frame.push(property)

    def __repr__(self) -> str:
        return f"Property({self.name})"

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.name == other.name


class GetProperty(Operation):
    """Get the value of a property from an object. The property primitive comes from the stack"""

    def execute(self, frame: "StackFrame") -> None:
        property = frame.pop()
        if not property.is_property:
            raise TypeError(f"Cannot get property of {property.type}")

        target, name = property.value

        result = Primitive.of(target.get(name, None))
        frame.push(result)
