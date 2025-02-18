from typing import Optional
import structlog

from probots.db import DB
from probots.models.all import BaseSchema, Program, User
from probots.probotics.compiler import ProboticsCompiler

LOGGER = structlog.get_logger(__name__)


class UserProgramUpdateRequest(BaseSchema):
    content: str
    parse: bool = False
    run: bool = False


class UserProgramUpdateResult(BaseSchema):
    parse_success: Optional[bool] = None
    parse_result: Optional[str] = None


class UserProgramUpdateResponse(BaseSchema):
    result: UserProgramUpdateResult


class ProgramService:
    def get_user_program(self, user: User) -> Program:
        return user.current_program

    def update_user_program(
        self, user: User, update: UserProgramUpdateRequest
    ) -> UserProgramUpdateResult:
        result = UserProgramUpdateResult()

        program = user.current_program
        program.content = update.content

        if update.parse:
            compiler = ProboticsCompiler()
            try:
                compiler.compile(program.content)
                result.parse_success = True
            except Exception as ex:
                result.parse_success = False
                result.parse_result = str(ex)

        if update.run and result.parse_success:
            # Pass it to the game engine, if present...
            from .game.engine import ENGINE

            player = ENGINE.player_for_user(user)
            if player:
                ENGINE.programming.update_player(player, program)
            else:
                LOGGER.error("No game engine available for user", user=user.name)

        return result
