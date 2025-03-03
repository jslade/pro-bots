from enum import Enum


def enum_string(enum_value: Enum) -> str:
    try:
        return enum_value.value
    except AttributeError:
        return str(enum_value)
