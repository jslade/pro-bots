from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class PrimitiveType(str, Enum):
    NULL = "null"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    OBJECT = "object"


@dataclass
class Primitive:
    """The result of some execution"""

    type: PrimitiveType
    value: int | float | str | list | dict | None

    @classmethod
    def of(cls, value: Any) -> "Primitive":
        if value is None:
            return Primitive(PrimitiveType.NULL, val=None)

        t = type(value)
        if t is int:
            return Primitive(PrimitiveType.INT, value)
        if t is float:
            return Primitive(PrimitiveType.FLOAT, value)
        if t is str:
            return Primitive(PrimitiveType.STRING, value)
        if t is list:
            return Primitive(PrimitiveType.LIST, value)
        if t is dict:
            return Primitive(PrimitiveType.OBJECT, value)


class UndefinedSymbol(Exception):
    pass


@dataclass
class StackFrame:
    scope_vars: dict[str, Primitive]
    args: dict[str, Primitive]
    parent: Optional["StackFrame"] = None

    operation: Optional["Operation"] = None

    def get(self, name: str) -> Primitive:
        try:
            return self.args.get(
                name,  # Get from args first
                self.scope_vars.get(
                    name,  # Get from local scope next
                    self.parent.get(
                        name  # Get from parent scope (if any) last
                    )
                    if self.parent
                    else None,
                ),
            )
        except KeyError:
            raise UndefinedSymbol(f"No value for {name}")


class Operation:
    """Base class for an operation that can be executed"""

    def expected_args(self) -> list[tuple[str, list[PrimitiveType]]]:
        return []

    def execute(self, frame: StackFrame) -> Primitive:
        raise NotImplementedError


class Immediate(Operation):
    """A terminal value in the parse tree that has an immediate value"""

    def __init__(self, value: Primitive) -> None:
        self.value = value

    def execute(self, frame: StackFrame) -> Primitive:
        return self.value
