from typing import TYPE_CHECKING, Optional

import structlog

from ...models.game.all import Player
from ...probotics.compiler import ProboticsCompiler
from ...probotics.interpreter import (
    BreakCallback,
    ExceptionCallback,
    ExecutionContext,
    ProboticsInterpreter,
    ResultCallback,
)
from ...probotics.ops.all import Operation, ScopeVars, StackFrame
from .builtins import BuiltinsService
from .processor import Work

if TYPE_CHECKING:
    from .engine import Engine

LOGGER = structlog.get_logger(__name__)


class Programming:
    """Service that manages code execution in the context of the game.
    There is a single instance of the parser / compiler to turn code into
    executable operations.

    There is a single instance of the interpreter that runs the code, one
    command at a time. It continuously re-schedules work in the progress to
    runs as long as there are contexts that are in progress
    """

    def __init__(self, engine: "Engine") -> None:
        self.engine = engine
        self.compiler = ProboticsCompiler()
        self.interpreter = ProboticsInterpreter()

        self.builtins = BuiltinsService(self.engine)

    def compile(self, code: str) -> list[Operation]:
        """Compile the code into operations -- determine whether it is syntactically
        valid"""
        return self.compiler.compile(code)

    def execute(
        self,
        *,
        operations: list[Operation],
        player: Player,
        globals: ScopeVars,
        on_result: Optional[ResultCallback] = None,
        on_exception: Optional[ExceptionCallback] = None,
        replace: Optional[bool] = True,
    ) -> ExecutionContext:
        """Evaluate the code for the given player"""

        def on_break(context: ExecutionContext, player: Player = player) -> None:
            self.on_break(player, context)

        context = self.create_context(
            player=player,
            globals=globals,
            operations=operations,
            on_result=on_result,
            on_exception=on_exception,
            on_break=on_break,
        )

        if replace and context.name is not None:
            # Only allow one context per player
            self.interpreter.remove(context.name)

        self.interpreter.add(context)
        self.ensure_running()

        return context

    def create_context(
        self,
        *,
        player: Player,
        globals: ScopeVars,
        operations: list[Operation],
        on_result: Optional[ResultCallback],
        on_exception: Optional[ExceptionCallback] = None,
        on_break: Optional[BreakCallback] = None,
    ) -> ExecutionContext:
        """Create a new execution context for the given player, using the given globals
        as the starting point"""

        return ExecutionContext(
            operations=operations,
            builtins=self.builtins.update_builtins(player),
            globals=globals,
            on_result=on_result,
            on_exception=on_exception,
            on_break=on_break,
            name=f"player:{player.name}",
        )

    def ensure_running(self) -> None:
        """Make sure the interpreter is running (has work scheduled)"""
        if not self.engine.processor.has_work_where(
            lambda w: isinstance(w, InterpreterWork)
        ):
            self.schedule_run()

    def schedule_run(self) -> None:
        self.engine.processor.add_work(
            self.run,
            critical=False,  # TODO: should be True?
            work_type=InterpreterWork,
        )

    def run(self) -> None:
        """Run the interpreter until there is no more work to do"""
        self.interpreter.execute_next()

        # If there are still contexts to run, reschedule this work
        if not self.interpreter.is_finished:
            self.schedule_run()

    def on_break(self, player: Player, context: ExecutionContext) -> None:
        """Called when a break point is hit in the interpreter.
        Since the point of the game is to run the code: award points
        for the amount of code that was executed.
        """
        self.engine.update_score(player, context.latest_operations)


class InterpreterWork(Work):
    """Work that runs the interpreter"""

    pass
