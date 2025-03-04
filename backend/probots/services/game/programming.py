from typing import TYPE_CHECKING, Optional

import structlog

from ...models.game.all import Player, ProgramState
from ...probotics.compiler import ProboticsCompiler
from ...probotics.interpreter import (
    BreakCallback,
    CompleteCallback,
    ExceptionCallback,
    ExecutionContext,
    ProboticsInterpreter,
    ResultCallback,
)
from ...probotics.ops.all import Immediate, Operation, Primitive, ScopeVars, StackFrame
from ..message_handlers.terminal_handler import TerminalOutput
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

        self.player_contexts: dict[str, ExecutionContext] = {}
        self.player_globals: dict[str, ScopeVars] = {}

    def reset(self) -> None:
        self.interpreter.stop_all()
        self.interpreter = ProboticsInterpreter()

        self.player_contexts.clear()
        self.player_globals.clear()

    def compile(self, code: str) -> list[Operation]:
        """Compile the code into operations -- determine whether it is syntactically
        valid"""
        return self.compiler.compile(code)

    def execute(
        self,
        *,
        operations: list[Operation],
        player: Player,
        on_result: Optional[ResultCallback] = None,
        on_exception: Optional[ExceptionCallback] = None,
        replace_program: bool = True,
        replace_globals: bool = True,
    ) -> ExecutionContext:
        """Evaluate the code for the given player"""

        def wrap_on_break(context: ExecutionContext, player: Player = player) -> None:
            self.on_break(player, context)
            player.program_state = (
                ProgramState.paused
                if self.is_player_waiting(player)
                else ProgramState.running
            )

        def wrap_on_result(
            result: Primitive, context: ExecutionContext, player: Player = player
        ) -> None:
            if on_result:
                on_result(result, context)

            # The context is done executing, remove it from the interpreter
            if self.player_contexts.get(player.name, None) == context:
                del self.player_contexts[player.name]

            # Award points for the amount of code that was executed
            self.engine.update_score(player, context.latest_operations)

        def wrap_on_exception(
            exception: Exception, context: ExecutionContext, player: Player = player
        ) -> None:
            player.program_state = ProgramState.not_running
            on_exception(exception, context)

        def wrap_on_complete(context: ExecutionContext, player: Player = player) -> None:
            player.program_state = (
                ProgramState.running
                if self.is_player_running(player)
                else ProgramState.not_running
            )

            self.engine.update_score(player, 0)

        context = self.create_context(
            player=player,
            operations=operations,
            on_result=wrap_on_result,
            on_exception=on_exception,
            on_break=wrap_on_break,
            on_complete=wrap_on_complete,
        )

        if replace_program and context.name is not None:
            # Only allow one named context per player
            # This allows for other un-named contexts, like from the terminal and
            # manual controls
            self.interpreter.remove(context.name)
            self.player_contexts[player.name] = context

        if replace_globals:
            self.get_player_globals(player).clear()

        self.interpreter.add(context)
        self.ensure_running()

        player.program_state = ProgramState.running
        return context

    def get_player_globals(self, player: Player) -> ScopeVars:
        """Get the globals for the player, creating them if they do not exist"""
        globals = self.player_globals.get(player.name, None)
        if globals is None:
            globals = ScopeVars()
            self.player_globals[player.name] = globals

        return globals

    def create_context(
        self,
        *,
        player: Player,
        operations: list[Operation],
        on_result: Optional[ResultCallback],
        on_exception: Optional[ExceptionCallback] = None,
        on_break: Optional[BreakCallback] = None,
        on_complete: Optional[CompleteCallback] = None,
    ) -> ExecutionContext:
        """Create a new execution context for the given player, using the given globals
        as the starting point"""

        return ExecutionContext(
            operations=operations,
            builtins=self.builtins.get_builtins(player),
            globals=self.get_player_globals(player),
            on_result=on_result,
            on_exception=on_exception,
            on_break=on_break,
            on_complete=on_complete,
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
            critical=True,
            work_type=InterpreterWork,
        )

    def run(self) -> None:
        """Run the interpreter until there is no more work to do"""
        self.interpreter.execute_next()

        # If there are still contexts to run, reschedule this work
        if not self.interpreter.is_finished:
            self.schedule_run()

    def is_player_running(self, player: Player) -> bool:
        context = self.player_contexts.get(player.name, None)
        return context is not None and not context.is_finished

    def is_player_waiting(self, player: Player) -> bool:
        context = self.player_contexts.get(player.name, None)
        return context is not None and context.stopped

    def suspend_player(self, player: Player) -> bool:
        context = self.player_contexts.get(player.name, None)
        if context is not None and not context.stopped:
            self.interpreter.stop(context)
            player.program_state = ProgramState.paused

    def resume_player(self, player: Player) -> bool:
        context = self.player_contexts.get(player.name, None)
        if context is not None and context.stopped:
            self.interpreter.resume(context)
            self.ensure_running()
            player.program_state = ProgramState.running

    def on_break(self, player: Player, context: ExecutionContext) -> None:
        """Called when a break point is hit in the interpreter.
        Since the point of the game is to run the code: award points
        for the amount of code that was executed.
        """
        self.engine.update_score(player, context.latest_operations)

    def emit_event(self, event: str, player: Player, args: ScopeVars) -> None:
        """Emit an event to the player. This will execute an event handler in the
        player's code, if one is defined."""

        context = self.player_contexts.get(player.name, None)
        # LOGGER.debug(
        #    "emit_event",
        #    name=event,
        #    player=player.name,
        #    args=args,
        #    running=self.is_player_running(player),
        #    waiting=self.is_player_waiting(player),
        #    context=context,
        #    is_finished=context.is_finished if context else None,
        #    frame=context.current_frame.describe()
        #    if context and context.current_frame
        #    else None,
        #    contexts=[(c.name, c.is_finished) for c in self.interpreter.contexts],
        #    player_contexts=[(p, c.is_finished) for p, c in self.player_contexts.items()],
        # )

        if self.is_player_running(player):
            # LOGGER.info(
            #    "emit_event - player is already running",
            #    name=event,
            #    user=player.name,
            #    player=player.display_name,
            # )
            return

        # Get the event handler
        # Don't do anything if the player does not have a handler defined
        if not self.has_callable(player, event):
            # LOGGER.debug(
            #    "emit_event - no handler", name=event, player=player.name, args=args
            # )
            return

        try:
            call = f"{event}()"
            operations = self.compiler.compile(call)

            # the call op is initially the second operation
            # - GetValue(event)
            # - Call()
            call_op = operations[1]
            call_op.num_args = len(args)

            # Put the call arguments onto the stack by creating immediate operations
            # These go after the GetValue(event) op, before the Call op
            immediate_args = [Immediate(arg_value) for arg_value in args.values()]
            while immediate_args:
                arg = immediate_args.pop()
                operations.insert(1, arg)

        except Exception as ex:
            LOGGER.exception(
                "emit_event - failed to compile",
                name=event,
                player=player.name,
                args=args,
                exception=ex,
            )
            return

        # LOGGER.debug(
        #    "emit_event - compiled",
        #    name=event,
        #    player=player.name,
        #    operations=operations,
        # )

        def on_exception(
            ex: Exception, context: ExecutionContext, frame: StackFrame
        ) -> None:
            LOGGER.info(
                "on_player_exception",
                user=player.name,
                player=player.display_name,
                ex=ex,
                frame=frame.describe(),
            )
            describe = f"Exception: {ex}\n{frame.describe()}"
            output = TerminalOutput(output=describe)
            self.engine.send_to_player(player, "terminal", "output", output.as_msg())

        # Execute the event handler
        self.execute(
            operations=operations,
            player=player,
            on_exception=on_exception,
            replace_program=True,  # can't have more than one context for the player
            replace_globals=False,
        )

    def has_callable(self, player: Player, name: str) -> bool:
        """Check if the player has a callable function with the given name"""
        player_globals = self.get_player_globals(player)
        handler = player_globals.get(name, None)
        return handler is not None and handler.is_block


class InterpreterWork(Work):
    """Work that runs the interpreter"""

    pass
