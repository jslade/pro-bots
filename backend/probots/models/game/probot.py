from pydantic import Field
from enum import Enum
from typing import ClassVar, Optional, Self


from ..mixins.pydantic_base import BaseSchema
from .player import Player
from .program import ProgramState
from .transition import Transition


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


class Probot(BaseSchema):
    MAX_ENERGY: ClassVar[int] = 1000

    player: Player

    id: int
    name: Optional[str]
    x: int
    y: int
    orientation: ProbotOrientation

    state: ProbotState
    energy: int
    crystals: int

    transitions: list[Transition] = []

    program_state: Optional[ProgramState] = Field(None, exclude=True)

    @classmethod
    def create_at(cls, player: Player, id: int, x: int, y: int) -> Self:
        return Probot(
            player=player,
            id=id,
            name=None,
            x=x,
            y=y,
            orientation=ProbotOrientation.N,
            energy=cls.MAX_ENERGY,
            crystals=0,
        )
