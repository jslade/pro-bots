from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Operation


class PrimitiveType(str, Enum):
    NULL = "null"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    PROPERTY = "property"
    LIST = "list"
    OBJECT = "object"
    SYMBOL = "symbol"
    BLOCK = "block"


@dataclass
class Primitive:
    """The result of some execution"""

    type: PrimitiveType
    value: int | float | str | list | dict | tuple[dict, str] | tuple[list, str] | None

    @property
    def is_true(self) -> bool:
        return bool(self.value)

    @property
    def is_null(self) -> bool:
        return self.type == PrimitiveType.NULL

    @property
    def is_symbol(self) -> bool:
        return self.type == PrimitiveType.SYMBOL

    @property
    def is_property(self) -> bool:
        return self.type == PrimitiveType.PROPERTY

    @property
    def is_object(self) -> bool:
        return self.type == PrimitiveType.OBJECT

    @property
    def is_list(self) -> bool:
        return self.type == PrimitiveType.LIST

    @property
    def is_block(self) -> bool:
        return self.type == PrimitiveType.BLOCK

    @classmethod
    def of(cls, value: Any) -> "Primitive":
        if value is None:
            return Primitive(PrimitiveType.NULL, None)

        t = type(value)
        if t is NoneType:
            return Primitive(PrimitiveType.NULL, None)
        if t is int:
            return Primitive(PrimitiveType.INT, value)
        if t is float:
            return Primitive(PrimitiveType.FLOAT, value)
        if t is str:
            return Primitive(PrimitiveType.STRING, value)
        if t is bool:
            return Primitive(PrimitiveType.BOOL, value)
        if t is list:
            return Primitive(PrimitiveType.LIST, value)
        if t is dict:
            return Primitive(PrimitiveType.OBJECT, value)
        if t is Primitive:
            return value

        raise TypeError(f"Cannot convert {t} to primitive")

    @classmethod
    def symbol(cls, name: str) -> "Primitive":
        return Primitive(PrimitiveType.SYMBOL, value=name)

    @classmethod
    def property(cls, target: dict, name: str) -> "Primitive":
        return Primitive(PrimitiveType.PROPERTY, value=(target, name))

    @classmethod
    def index(cls, target: list, idx: int) -> "Primitive":
        return Primitive(PrimitiveType.PROPERTY, value=(target, idx))

    @classmethod
    def block(
        cls,
        operations: list["Operation"],
        name: Optional[str] = None,
        arg_names: Optional[list[str]] = None,
    ) -> "Primitive":
        from .call import Block

        block = Block(operations=operations, name=name, arg_names=arg_names or [])
        return Primitive(PrimitiveType.BLOCK, value=block)
