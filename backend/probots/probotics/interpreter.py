from typing import Callable, Optional, TypeAlias

import structlog

from .ops.all import Operation, Primitive, StackFrame, Breakpoint, EnterScope, ExitScope

LOGGER = structlog.get_logger(__name__)


ResultCallback: TypeAlias = Callable[[Primitive], None]


class ExecutionContext:
    def __init__(self, *, operations: list[Operation], on_result: ResultCallback) -> None:
        self.builtins: dict[str, Primitive] = {}
        self.operations = operations
        self.on_result = on_result

        self.current: Optional[StackFrame] = None

    def execute_next(self) -> bool:
        """Execute one operation. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        if self.current is None:
            self.current = StackFrame.make_outer(
                self.operations,
                self.builtins,
            )

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
        except EnterScope as enter_scope:
            LOGGER.debug("Entering scope", frame=enter_scope.frame.name)
            frame = enter_scope.frame
        except ExitScope as exit_scope:
            LOGGER.debug("Exiting scope", frame=exit_scope.frame.name)
            frame = exit_scope.frame.parent
            if frame:
                # Current frame gets the return value of the scope that just exited
                frame.push(exit_scope.return_value)
            else:
                # We just executed the outermost frame,
                self.on_result(exit_scope.return_value)
        except Exception as ex:
            LOGGER.exception("Execution error", exception=ex)
            raise ex

    def execute_frame(self, frame: StackFrame) -> None:
        """Execute the next operations in the frame, until something
        causes a break (breakpoint, enter scope, exit scope)"""
        while True:
            op = frame.next_op()

            LOGGER.debug("Executing operation", operation=op)
            op.execute(frame)

    @property
    def is_finished(self) -> bool:
        return self.current is None


class ProboticsInterpreter:
    def __init__(self) -> None:
        self.contexts: list[ExecutionContext] = []

    def add(self, context: ExecutionContext) -> None:
        self.contexts.append(context)

    def execute_next(self) -> None:
        """Execute the next sequence of operations. If the operation contains nested
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
