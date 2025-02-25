from typing import Callable, Optional, TypeAlias

import structlog

from .ops.all import (
    Breakpoint,
    Catch,
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
BreakCallback: TypeAlias = Callable[["ExecutionContext"], None]


class ExecutionContext:
    builtins: ScopeVars
    operations: list[Operation]
    globals: ScopeVars
    on_result: Optional[ResultCallback]
    on_exception: Optional[ExceptionCallback]
    on_break: Optional[BreakCallback]

    current_frame: Optional[StackFrame]
    stopped: bool

    total_frames: int
    total_operations: int

    latest_frames: int
    latest_operations: int

    name: Optional[str] = None

    def __init__(
        self,
        *,
        operations: list[Operation],
        builtins: ScopeVars = None,
        globals: Optional[ScopeVars] = None,
        on_result: Optional[ResultCallback] = None,
        on_exception: Optional[ExceptionCallback] = None,
        on_break: Optional[BreakCallback] = None,
        name: Optional[str] = None,
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

        # Callback to be called when a breakpoint is hit
        self.on_break = on_break

        # Globals are symbols can be assigned to in the outer scope only,
        # and will stay around as long as this execution context exists
        self.globals = globals or ScopeVars()

        self.name = name

        self.current_frame: Optional[StackFrame] = None
        self.stopped = False

        self.total_frames = 0
        self.total_operations = 0
        self.latest_frames = 0
        self.latest_operations = 0

    def execute_next(self) -> bool:
        """Execute one operation. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        if self.stopped:
            return self.is_finished

        if self.current_frame is None:
            self.current_frame = StackFrame.make_outer(
                self, self.operations, self.builtins, self.globals
            )

        self.current_frame = self.execute_until_break(self.current_frame)

        if self.on_break:
            self.on_break(self)

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

        except EnterScope as enter_scope:
            # LOGGER.debug("Entering scope", frame=enter_scope.frame.name)
            return enter_scope.frame

        except ExitScope as exit_scope:
            # LOGGER.debug("Exiting scope", frame=exit_scope.frame.name)
            frame = exit_scope.frame.parent
            if frame:
                # Current frame gets the return value of the scope that just exited
                if exit_scope.return_value is not None:
                    frame.push(exit_scope.return_value)
                return frame
            else:
                # We just exited the outermost frame,
                if exit_scope.return_value is not None:
                    self.on_result(exit_scope.return_value, self)

        except Breakpoint as bp:
            next_frame = self.handle_breakpoint(frame, bp)
            if next_frame is None:
                LOGGER.debug("Breakpoint not handled")
                raise

            # LOGGER.debug("Breakpoint handled", frame=next_frame.name)
            return next_frame

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

            # LOGGER.debug("Executing operation", operation=op)
            op.execute(frame)

            self.latest_operations += 1
            self.total_operations += 1

    def handle_breakpoint(
        self, frame: StackFrame, bp: Breakpoint
    ) -> Optional[StackFrame]:
        """Handle a breakpoint. Traverse up the stack until we find a catcher that
        handles this specific breakpoint. If we find one, that is the frame to continue
        execution on.
        """
        # LOGGER.debug("Breakpoint hit", reason=bp.reason)

        if bp.stop:
            self.stop()
            return frame

        next_frame = frame.parent
        while next_frame is not None:
            # Is the next op in the frame a catcher?
            if isinstance(catcher := next_frame.peek_op(), Catch):
                jump = catcher.jumps.get(bp.reason, None)
                if jump is not None:
                    # This catcher handles the breakpoint:
                    catcher.do_jump(jump, next_frame)
                    return next_frame

            next_frame = next_frame.parent

        # No catcher found
        return None

    def stop(self) -> None:
        self.stopped = True

    def resume(self) -> None:
        self.stopped = False

    @property
    def is_finished(self) -> bool:
        return self.current_frame is None

    def get(self, name: str) -> Primitive:
        """Get the value of a symbol in the outer scope (globals)"""
        return self.globals.get(name, Primitive.of(None))


class ProboticsInterpreter:
    def __init__(self) -> None:
        self.contexts: list[ExecutionContext] = []
        self.stopped_contexts: list[ExecutionContext] = []

    def add(self, context: ExecutionContext) -> None:
        self.contexts.append(context)

    def remove(self, name: str) -> None:
        index = next((i for i, c in enumerate(self.contexts) if c.name == name), None)
        if index is not None:
            self.contexts.pop(index)

    def execute_next(self) -> None:
        """Execute the next sequence of operations. If the operation contains nested
        operations, it may stop when an appropriate break point is hit, for the
        purpose of other interpreters to run"""
        try:
            context = self.contexts.pop(0)
        except IndexError:
            context = None

        if context is None:
            # LOGGER.info("No more contexts to execute")
            return

        try:
            finished = context.execute_next()
            if not finished:
                if context.stopped:
                    self.stopped_contexts.append(context)
                else:
                    self.contexts.append(context)
        except Exception as ex:
            LOGGER.exception("Execution error", exception=ex)
            raise ex

    def stop(self, context: ExecutionContext) -> None:
        if context not in self.stopped_contexts:
            self.stopped_contexts.append(context)
            context.stop()

    def resume(self, context: ExecutionContext) -> None:
        if context in self.stopped_contexts:
            self.stopped_contexts.remove(context)
            context.resume()
            self.contexts.append(context)

    @property
    def is_finished(self) -> bool:
        return len(self.contexts) == 0 and len(self.stopped_contexts) == 0
