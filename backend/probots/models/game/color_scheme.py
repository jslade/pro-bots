from ..mixins.pydantic_base import BaseSchema


class ColorScheme(BaseSchema):
    body: str
    head: str
    tail: str
