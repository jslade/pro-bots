from typing import Optional

from ..mixins.pydantic_base import BaseSchema
from .color_scheme import ColorScheme
from .program import ProgramState


class Player(BaseSchema):
    """A "player" in the game is the entity that is controlling a Probot
    (and potentially controlling other things in the future).

    A player most often will correspond to a human player, but it can also be
    used for computer-controlled entities.

    A player's behavior is defined by the program it is running."""

    name: str
    display_name: str

    score: int = 0
    program_state: ProgramState = ProgramState.not_running

    colors: ColorScheme = None

    session_id: Optional[str] = None
