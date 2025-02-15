from typing import Callable, Optional, TypeAlias

import structlog

from .ops.all import Operation, Primitive, StackFrame

LOGGER = structlog.get_logger(__name__)


class Breakpoint(Exception):
    """Exception to be raised when a breakpoint is hit during execution.
    This allows the context to stop and let other contexts run.
    """

    def __init__(self, message: str, frame: StackFrame) -> None:
        super().__init__(message)
        self.message = message
        self.frame = frame


ResultCallback: TypeAlias = Callable[[Primitive], None]


class ExecutionContext:
    def __init__(self, *, operations: list[Operation], on_result: ResultCallback) -> None:
        self.operations = operations
        self.on_result = on_result

        self.current: Optional[StackFrame] = None

    def execute_next(self) -> bool:
        """Execute one operation. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        if self.current is None:
            self.current = self.make_outer_frame(self.operations.pop(0))

        self.current = self.execute_until_break(self.current)

        return self.is_finished

    def execute_until_break(self, frame: StackFrame) -> Optional[StackFrame]:
        """Execute the frame, either until completion or to the next breakpoint.
        If stopped at a breakpoint, return the operation to be executed on the
        next iteration"""

        try:
            while frame is not None:
                self.execute_frame(frame)
                frame = frame.parent
            return None  # completed this frame / operation
        except Breakpoint as bp:
            LOGGER.debug("Breakpoint hit", message=bp.message, frame=bp.frame)
            # Return the operation that was executed when the breakpoint was hit,
            # that's where it will continue on the next iteration
            return bp.frame
        except Exception as ex:
            LOGGER.exception("Execution error", exception=ex)
            raise ex

    def make_outer_frame(self, op: Operation) -> StackFrame:
        """Create a stack frame for the operation. This will always be an outer
        frame with no parent, so the only scope vars are the global ones"""
        frame = StackFrame(
            # TODO: populate global vars
            scope_vars={},
            args={},
            operation=op,
        )
        return frame

    def execute_frame(self, frame: StackFrame) -> None:
        """Execute the operation in the frame. This will either return a
        Primitive value or raise an exception"""
        op = frame.operation
        if op is None:
            raise ValueError("No operation to execute")

        result = op.execute(frame)
        self.on_result(result)

    @property
    def is_finished(self) -> bool:
        return self.current is None and len(self.operations) == 0


class ProboticsInterpreter:
    def __init__(self) -> None:
        self.contexts: list[ExecutionContext] = []

    def add(self, context: ExecutionContext) -> None:
        if not context.is_finished:
            self.contexts.append(context)

    def execute_next(self) -> None:
        """Execute one operation. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        context = self.contexts.pop(0)
        if context is None:
            LOGGER.info("No more contexts to execute")
            return

        try:
            finished = context.execute_next()
            if not finished:
                self.contexts.append(context)
        except Exception as ex:
            LOGGER.exception("Execution error", exception=ex)
            raise ex
