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
        """Handle manual input from the terminal -- special commands that are not
        implemented in the probotics language."""

        # ... currently nothing ...

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
        LOGGER.debug(
            "Executing input",
            input=input.input,
            session=session.id,
            operations=operations,
        )

        def on_result(result: Primitive, context: ExecutionContext) -> None:
            """Called when there is a result from the interpreter"""
            LOGGER.info(
                "on_player_result",
                player=player.name,
                result=result,
            )
            if result:
                output = TerminalOutput(output=Primitive.output(result.value))
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
            on_result=on_result,
            on_exception=on_exception,
            replace=False,
        )

        # Points just for executing something via the terminal
        ENGINE.update_score(player, 5)

        return True
