from typing import TYPE_CHECKING, Optional

import structlog

from ...models.game.all import Player
from ...probotics.compiler import ProboticsCompiler
from ...probotics.interpreter import (
    ExecutionContext,
    ProboticsInterpreter,
    ResultCallback,
)
from ...probotics.ops.all import Operation, Primitive, ScopeVars
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

        # These built-ins get added to every context automatically
        # TODO: Define builtins
        self.builtins: ScopeVars = {}

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
    ) -> ExecutionContext:
        """Evaluate the code for the given player"""
        context = self.create_context(
            player=player, globals=globals, operations=operations, on_result=on_result
        )

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
    ) -> ExecutionContext:
        """Create a new execution context for the given player, using the given globals
        as the starting point"""

        def on_result_wrapper(result: Primitive, context: ExecutionContext):
            self.on_player_result(player, result, context, on_result)

        return ExecutionContext(
            operations=operations,
            builtins=self.builtins,
            globals=globals,
            on_result=on_result,
        )

    def on_player_result(
        self,
        player: Player,
        result: Primitive,
        context: ExecutionContext,
        on_result: Optional[ResultCallback],
    ) -> None:
        """Called when there is a result from the interpreter"""
        LOGGER.info("on_player_result", player=player, result=result)
        if on_result:
            on_result(result, context)

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


class InterpreterWork(Work):
    """Work that runs the interpreter"""

    pass
