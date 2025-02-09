from ..mixins.pydantic_base import BaseSchema


class Program(BaseSchema):
    """A Probotics program that has been parsed into runnable code,
    along with the runtime data associated with it."""

    source: str

    # TODO:
    # add the AST, instruction pointer, stack etc
