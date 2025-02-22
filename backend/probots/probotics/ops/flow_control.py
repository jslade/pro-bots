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
        self.do_jump(self.jump, frame)

    def do_jump(self, jump: int, frame: StackFrame) -> None:
        frame.op_index += jump
        if frame.op_index < 0 or frame.op_index > len(frame.operations):
            # import ipdb

            # ipdb.set_trace()
            raise ValueError("Jump index out of bounds")

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.jump == other.jump

    def __repr__(self) -> str:
        return f"Jump(jump={self.jump})"


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
        if not super().__eq__(other):
            return False
        return self.jump == other.jump and self.sense == other.sense

    def __repr__(self) -> str:
        return f"JumpIf(jump={self.jump}, sense={self.sense})"


class Breakpoint(Exception):
    """Exception to be raised when a breakpoint is hit during execution.
    This allows the context to stop and let other contexts run.
    """

    reason: str
    stop: bool

    def __init__(self, *, reason: str, stop: bool = False) -> None:
        super().__init__()
        self.reason = reason
        self.stop = stop


class Break(Operation):
    """Break out of the current frame by raising a breakpoint.
    This will cause the interpreter to unwind the stack until it finds a Catch"""

    def execute(self, frame: StackFrame) -> None:
        raise Breakpoint(reason="break")


class Next(Operation):
    """Break out of the current frame by raising a breakpoint.
    This will cause the interpreter to unwind the stack until it finds a Catch"""

    def execute(self, frame: StackFrame) -> None:
        raise Breakpoint(reason="next")


class Catch(Jump):
    """catch a breakpoint. Execute a jump based on what is caught"""

    jumps: dict[str, int]

    def __init__(self, jumps: dict[str, int]) -> None:
        super().__init__(0)
        self.jumps = jumps

    def execute(self, frame: StackFrame) -> None:
        # When this op is executed, it doesn't do anything. It exists
        # to be used by the interpreter to handle breakpoint exceptions.
        pass

    def catches(self, reason: str) -> bool:
        return reason in self.jumps

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.jumps == other.jumps

    def __repr__(self) -> str:
        return f"Catch(jumps={self.jumps})"
