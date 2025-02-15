from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Any, Optional


class PrimitiveType(str, Enum):
    NULL = "null"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    LIST = "list"
    OBJECT = "object"
    SYMBOL = "SYMBOL"


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

    @classmethod
    def symbol(cls, name: str) -> "Primitive":
        return Primitive(PrimitiveType.SYMBOL, value=name)
