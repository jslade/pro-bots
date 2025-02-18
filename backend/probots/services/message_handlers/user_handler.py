from typing import Optional

import structlog

from ...db import DB
from ...models.all import Message, Program, Session
from ...models.mixins.pydantic_base import BaseSchema
from ...probotics.interpreter import ExecutionContext
from ...probotics.ops.primitive import Primitive
from ...probotics.ops.stack_frame import ScopeVars, StackFrame
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from .base import MessageHandler

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
    def __init__(self) -> None:
        super().__init__()
        self.session_globals: dict[str, ScopeVars] = {}

    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("user", "get_program", self.handle_get_program)
        dispatcher.register_handler("user", "update_program", self.handle_update_program)

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
            compiled=compiled,
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
            program = Program(user=user)
            DB.session.add(program)

        content = update_request.program
        program.content = content

        DB.session.commit()

        did_run = False

        compiled, error = self.compile(content)
        response = UpdateProgramResponse(
            compiled=compiled,
            error=error,
            run=did_run,
        )
        dispatcher.send(session, "user", "update_program", response.as_msg())

        # Easy way to show error for now:
        if not compiled:
            from .terminal_handler import TerminalOutput

            lines = error.splitlines()
            term_output = TerminalOutput(output="\n".join(lines[0:3]))
            dispatcher.send(session, "terminal", "output", term_output.as_msg())

    def compile(self, content: str) -> tuple[bool, Optional[str]]:
        try:
            ENGINE.programming.compile(content)
            return True, None
        except Exception as ex:
            # LOGGER.exception("Compilation error", exception=ex)
            return False, str(ex)
