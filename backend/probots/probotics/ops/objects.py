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


class Index(Operation):
    """Create a reference to an index of a list, or an object property. This is similar
    to Property(), except that the index can be a string or an integer, and it is
    popped form the stack vs known at compile time."""

    def execute(self, frame: "StackFrame") -> None:
        index = frame.pop()
        target = frame.pop()

        if target.is_object and type(index.value) is str:
            result = Primitive.property(target.value, index.value)
        elif target.is_list and type(index.value) is int:
            result = Primitive.property(target.value, index.value)
        else:
            raise TypeError(f"Cannot index {target.type} with {index.type}")

        frame.push(result)


class GetIndex(Operation):
    """Get the value of an index from a list, or an object property. The index primitive comes from the stack"""

    def execute(self, frame: "StackFrame") -> None:
        index = frame.pop()
        if not index.is_property:
            raise TypeError(f"Cannot get index of {index.type}")

        target, idx = index.value

        if type(target) is dict:
            result = Primitive.of(target.get(idx, None))
        elif type(target) is list:
            try:
                result = Primitive.of(target[idx])
            except IndexError:
                result = Primitive.of(None)

        frame.push(result)
