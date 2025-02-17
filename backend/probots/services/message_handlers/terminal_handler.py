import structlog

from ...models.all import Message, Session
from ...models.mixins.pydantic_base import BaseSchema
from ...probotics.interpreter import ExecutionContext
from ...probotics.ops.primitive import Primitive
from ...probotics.ops.stack_frame import ScopeVars, StackFrame
from ..dispatcher import Dispatcher
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class TerminalInput(BaseSchema):
    input: str


class TerminalOutput(BaseSchema):
    output: str


class TerminalHandler(MessageHandler):
    def __init__(self) -> None:
        super().__init__()
        self.session_globals: dict[str, ScopeVars] = {}

    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("terminal", "input", self.handle_input)

    def handle_input(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        input = TerminalInput(**message.data)

        LOGGER.info(
            "Terminal input",
            input=input.input,
            session=session.id,
        )

        if self.handle_manual_input(session, input, dispatcher):
            return

        if self.handle_exec_input(session, input, dispatcher):
            return

    def handle_manual_input(
        self, session: Session, input: TerminalInput, dispatcher: Dispatcher
    ) -> bool:
        from ..game.engine import ENGINE

        """Handle manual input from the terminal -- special commands that are not
        implemented in the probotics language."""
        # TODO: Just for testing
        if input.input == "map":
            if grid := ENGINE.grid:
                output = TerminalOutput(output=grid.to_str())
            else:
                output = TerminalOutput(output="n/a")
            dispatcher.send(session, "terminal", "output", output.as_msg())
            return True

        # TODO: Just for testing. Eventually this will be handled via probotics
        if input.input.startswith("move"):
            backward = False
            bonus = 5

            words = input.input.split()
            if len(words) > 1:
                if words[1].startswith("back"):
                    backward = True
                    bonus = 10

            probot = ENGINE.probot_for_session(session)
            if probot:
                ENGINE.mover.move(probot, backward=backward, bonus=bonus)
            return True

        # TODO: Just for testing. Eventually this will be handled via probotics
        if input.input.startswith("turn"):
            words = input.input.split()
            if len(words) > 1:
                dir = words[1]

                probot = ENGINE.probot_for_session(session)
                if probot:
                    ENGINE.mover.turn(probot, dir=dir, bonus=3)
            return True

        return False

    def handle_exec_input(
        self, session: Session, input: TerminalInput, dispatcher: Dispatcher
    ) -> bool:
        from ..game.engine import ENGINE

        player = ENGINE.player_for_session(session)
        if not player:
            return False

        # Ensure it is valid input
        try:
            operations = ENGINE.programming.compile(input.input)
        except Exception as e:
            output = TerminalOutput(output=f"Error: {e}")
            dispatcher.send(session, "terminal", "output", output.as_msg())
            return True

        # Compiled, so execute it
        # Result will be sent to the player asynchronously via the on_result callback
        globals = self.session_globals.get(session.id, None)
        if globals is None:
            globals = ScopeVars()
            self.session_globals[session.id] = globals

        LOGGER.debug(
            "Executing input",
            input=input.input,
            session=session.id,
            globals=globals,
            operations=operations,
        )

        def on_result(result: Primitive, context: ExecutionContext) -> None:
            """Called when there is a result from the interpreter"""
            LOGGER.info(
                "on_player_result",
                player=player.name,
                result=result,
            )
            self.session_globals[session.id] = context.globals
            output = TerminalOutput(output=str(result.value))
            dispatcher.send(session, "terminal", "output", output.as_msg())

        def on_exception(
            ex: Exception, context: ExecutionContext, frame: StackFrame
        ) -> None:
            """Called when there is an exception during execution in the interpreter"""
            LOGGER.info(
                "on_player_exception",
                player=player.name,
                ex=ex,
            )
            output = TerminalOutput(output=str(ex))
            dispatcher.send(session, "terminal", "output", output.as_msg())

        ENGINE.programming.execute(
            operations=operations,
            player=player,
            globals=globals,
            on_result=on_result,
            on_exception=on_exception,
        )

        return True
