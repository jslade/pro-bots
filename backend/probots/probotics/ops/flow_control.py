from .base import Operation
from .stack_frame import StackFrame


class Jump(Operation):
    """Jump (goto) a new instruction location unconditionally.
    This is used to implement if and while statements."""

    jump: int

    def __init__(self, jump: int):
        super().__init__()
        self.jump = jump

    def execute(self, frame: StackFrame) -> None:
        # NB: At the time this operation is executed, the frame's instruction pointer
        # is already at the next instruction. So care is needed in determining the jump
        frame.op_index += self.jump
        if frame.op_index < 0 or frame.op_index > len(frame.operations):
            raise ValueError("Jump index out of bounds")

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.jump == other.jump

    def __repr__(self) -> str:
        return f"JumpIf({self.jump})"


class JumpIf(Jump):
    """Jump (goto) a new instruction location if the top of the stack is true.
    This is used to implement if and while statements."""

    sense: bool

    def __init__(self, jump: int, sense: bool = True):
        super().__init__(jump=jump)
        self.sense = sense

    def execute(self, frame: StackFrame) -> None:
        condition = frame.pop()
        if condition.is_true is self.sense:
            super().execute(frame)

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.jump == other.jump

    def __repr__(self) -> str:
        return f"JumpIf({self.jump})"
