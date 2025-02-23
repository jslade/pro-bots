from typing import Optional

import structlog

from ...db import DB
from ...models.all import Message, Program, Session
from ...models.mixins.pydantic_base import BaseSchema
from ...probotics.interpreter import ExecutionContext
from ...probotics.ops.base import Operation
from ...probotics.ops.primitive import Primitive
from ...probotics.ops.stack_frame import StackFrame
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from .base import MessageHandler
from .terminal_handler import TerminalOutput

LOGGER = structlog.get_logger(__name__)


class GetProgramRequest(BaseSchema):
    pass


class GetProgramResponse(BaseSchema):
    program: str
    compiled: bool
    error: Optional[str]


class UpdateProgramRequest(BaseSchema):
    program: str
    compile: bool = True
    run: bool = False


class UpdateProgramResponse(BaseSchema):
    compiled: bool
    error: Optional[str]
    run: bool


class UserHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("user", "get_program", self.handle_get_program)
        dispatcher.register_handler("user", "update_program", self.handle_update_program)
        dispatcher.register_handler("user", "stop_program", self.handle_stop_program)

    def handle_get_program(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        # get_request = GetProgramRequest(**message.data)

        LOGGER.info(
            "Get program request",
            session=session.id,
        )

        user = session.user
        content = user.current_program.content if user.current_program else ""

        compiled, error = self.compile(content)
        response = GetProgramResponse(
            program=content,
            compiled=compiled is not None,
            error=error,
        )
        dispatcher.send(session, "user", "get_program", response.as_msg())

    def handle_update_program(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        update_request = UpdateProgramRequest(**message.data)

        LOGGER.info(
            "Update program request",
            session=session.id,
        )

        user = session.user
        program = user.current_program
        if not user.current_program:
            program = Program(user=user, content="// Write your code here")
            DB.session.add(program)

        content = update_request.program
        program.content = content

        DB.session.commit()

        did_run = False

        compiled, error = self.compile(content)

        if update_request.run:
            did_run = self.run(session, compiled, dispatcher)

        response = UpdateProgramResponse(
            compiled=compiled is not None,
            error=error,
            run=did_run,
        )
        dispatcher.send(session, "user", "update_program", response.as_msg())

        # Easy way to show error for now:
        if not compiled:
            lines = error.splitlines()
            term_output = TerminalOutput(output="\n".join(lines[0:3]))
            dispatcher.send(session, "terminal", "output", term_output.as_msg())

    def compile(self, content: str) -> tuple[Optional[list[Operation]], Optional[str]]:
        try:
            operations = ENGINE.programming.compile(content)
            return operations, None
        except Exception as ex:
            # LOGGER.exception("Compilation error", exception=ex)
            return None, str(ex)

    def run(
        self, session: Session, compiled: list[Operation], dispatcher: Dispatcher
    ) -> bool:
        player = ENGINE.player_for_session(session)

        LOGGER.debug(
            "Executing user script",
            session=session.id,
        )

        def on_result(result: Primitive, context: ExecutionContext) -> None:
            """Called when there is a result from the interpreter"""
            LOGGER.info(
                "on_player_result",
                player=player.name,
                result=result,
            )
            if result is not None:
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
            operations=compiled,
            player=player,
            on_result=on_result,
            on_exception=on_exception,
            replace=True,
        )

        # Points for successfully executing a script -- that is the
        # purpose of the game, after all
        ENGINE.update_score(player, 100)

        return True

    def handle_stop_program(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        LOGGER.info(
            "Stop program request",
            session=session.id,
        )

        content = ""
        compiled, _ = self.compile(content)
        self.run(session, compiled, dispatcher)
