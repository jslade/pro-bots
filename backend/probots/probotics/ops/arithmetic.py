from .base import Operation, Primitive, PrimitiveType, StackFrame


class Addition(Operation):
    def expected_args(self) -> list[str]:
        return [
            ("left", (PrimitiveType.INT, PrimitiveType.FLOAT, PrimitiveType.STRING)),
            ("right", (PrimitiveType.INT, PrimitiveType.FLOAT, PrimitiveType.STRING)),
        ]

    def execute(self, frame: StackFrame) -> Primitive:
        left = frame.get("left")
        right = frame.get("right")
        result = left + right
        return Primitive.of(result)


class Subtraction(Operation):
    def expected_args(self) -> list[str]:
        return [
            ("left", (PrimitiveType.INT, PrimitiveType.FLOAT)),
            ("right", (PrimitiveType.INT, PrimitiveType.FLOAT)),
        ]

    def execute(self, frame: StackFrame) -> Primitive:
        left = frame.get("left")
        right = frame.get("right")
        result = left - right
        return Primitive.of(result)


class Multiplication(Operation):
    def expected_args(self) -> list[str]:
        return [
            ("left", (PrimitiveType.INT, PrimitiveType.FLOAT)),
            ("right", (PrimitiveType.INT, PrimitiveType.FLOAT)),
        ]

    def execute(self, frame: StackFrame) -> Primitive:
        left = frame.get("left")
        right = frame.get("right")
        result = left * right
        return Primitive.of(result)


class Division(Operation):
    def expected_args(self) -> list[str]:
        return [
            ("left", (PrimitiveType.INT, PrimitiveType.FLOAT)),
            ("right", (PrimitiveType.INT, PrimitiveType.FLOAT)),
        ]

    def execute(self, frame: StackFrame) -> Primitive:
        left = frame.get("left")
        right = frame.get("right")
        result = left / right
        return Primitive.of(result)
