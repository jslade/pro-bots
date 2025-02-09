from ..mixins.pydantic_base import BaseSchema


class Program(BaseSchema):
    """A Probotics program that has been parsed into runnable code"""

    source: str

    # TODO:
    # add the AST, instruction pointer, stack etc


class ProgramState(BaseSchema):
    """The runtime execution state of the program"""

    program: Program
