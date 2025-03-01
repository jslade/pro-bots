from enum import Enum
from typing import ClassVar, Optional

from pydantic import Field, field_serializer

from ..mixins.pydantic_base import BaseSchema
from .color_scheme import ColorScheme
from .player import Player
from .program import ProgramState


class ProbotOrientation(str, Enum):
    N = "N"
    W = "W"
    E = "E"
    S = "S"


class ProbotState(str, Enum):
    idle = "idle"
    moving = "moving"
    jumping = "jumping"
    turning = "turning"
    collecting = "collecting"
    saying = "saying"


class Probot(BaseSchema):
    MAX_ENERGY: ClassVar[int] = 1000
    MAX_CRYSTALS: ClassVar[int] = 1000

    player: Player
    colors: ColorScheme

    id: int
    name: Optional[str]
    x: int
    y: int
    orientation: ProbotOrientation

    state: ProbotState
    energy: int
    crystals: int

    # For transitioning
    dx: Optional[float] = 0
    dy: Optional[float] = 0
    dorient: Optional[float] = 0

    program_state: Optional[ProgramState] = Field(None, exclude=True)

    @property
    def position(self) -> tuple[int, int, ProbotOrientation]:
        return (self.x, self.y, self.orientation)

    @field_serializer("player")
    def serializer_player(self, player: Player) -> str:
        return player.name
