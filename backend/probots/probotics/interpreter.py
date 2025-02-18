from typing import Callable, Optional, TypeAlias

import structlog

from .ops.all import (
    Breakpoint,
    EnterScope,
    ExitScope,
    Operation,
    Primitive,
    ScopeVars,
    StackFrame,
)

LOGGER = structlog.get_logger(__name__)


ResultCallback: TypeAlias = Callable[[Primitive, "ExecutionContext"], None]
ExceptionCallback: TypeAlias = Callable[
    [Exception, "ExecutionContext", "StackFrame"], None
]


class ExecutionContext:
    builtins: ScopeVars
    operations: list[Operation]
    globals: ScopeVars
    on_result: Optional[ResultCallback]
    on_exception: Optional[ExceptionCallback]

    total_frames: int
    total_operations: int

    latest_frames: int
    latest_operations: int

    def __init__(
        self,
        *,
        operations: list[Operation],
        builtins: ScopeVars = None,
        globals: Optional[ScopeVars] = None,
        on_result: Optional[ResultCallback] = None,
        on_exception: Optional[ExceptionCallback] = None,
    ) -> None:
        # Builtins are symbols that cannot be changed (assigned to or overridden
        # by another global of the same name
        self.builtins = builtins or ScopeVars()

        # This is the program (list of operations that will be executed in the
        # outer scope
        self.operations = operations

        # Callback to be called when there is a result available in the
        # outer scope, used to pass results back to the caller
        self.on_result = on_result

        # Callback to be called when there is an exception when executing operations,
        # potentially in a nested scope
        self.on_exception = on_exception

        # Globals are symbols can be assigned to in the outer scope only,
        # and will stay around as long as this execution context exists
        self.globals = globals or ScopeVars()

        self.current_frame: Optional[StackFrame] = None

        self.total_frames = 0
        self.total_operations = 0
        self.latest_frames = 0
        self.latest_operations = 0

    def execute_next(self) -> bool:
        """Execute one operation. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        if self.current_frame is None:
            self.current_frame = StackFrame.make_outer(
                self.operations, self.builtins, self.globals
            )

        self.current_frame = self.execute_until_break(self.current_frame)

        return self.is_finished

    def execute_until_break(self, frame: StackFrame) -> Optional[StackFrame]:
        """Execute the frame, either until completion or to the next breakpoint.
        If stopped at a breakpoint, return the operation to be executed on the
        next iteration"""

        self.latest_frames = 0
        self.latest_operations = 0

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
            return enter_scope.frame
        except ExitScope as exit_scope:
            LOGGER.debug("Exiting scope", frame=exit_scope.frame.name)
            frame = exit_scope.frame.parent
            if frame:
                # Current frame gets the return value of the scope that just exited
                frame.push(exit_scope.return_value)
                return frame
            else:
                # We just executed the outermost frame,
                self.on_result(exit_scope.return_value, self)
        except Exception as ex:
            LOGGER.exception("Execution error", exception=ex)
            if self.on_exception:
                try:
                    self.on_exception(ex, self, frame)
                except Exception as ex2:
                    LOGGER.exception("Exception in exception handler", exception=ex2)

    def execute_frame(self, frame: StackFrame) -> None:
        """Execute the next operations in the frame, until something
        causes a break (breakpoint, enter scope, exit scope)"""

        self.latest_frames += 1
        self.total_frames += 1

        while True:
            op = frame.next_op()

            LOGGER.debug("Executing operation", operation=op)
            op.execute(frame)

            self.latest_operations += 1
            self.total_operations += 1

    @property
    def is_finished(self) -> bool:
        return self.current_frame is None

    def get(self, name: str) -> Primitive:
        """Get the value of a symbol in the outer scope (globals)"""
        return self.globals.get(name, Primitive.of(None))


class ProboticsInterpreter:
    def __init__(self) -> None:
        self.contexts: list[ExecutionContext] = []

    def add(self, context: ExecutionContext) -> None:
        self.contexts.append(context)

    def execute_next(self) -> None:
        """Execute the next sequence of operations. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        try:
            context = self.contexts.pop(0)
        except IndexError:
            context = None

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

    @property
    def is_finished(self) -> bool:
        return len(self.contexts) == 0
