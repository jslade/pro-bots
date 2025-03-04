from typing import TYPE_CHECKING

import structlog

from .....models.all import Program, User
from .....models.game.all import Player, Probot
from .....probotics.ops.all import Native, Operation, Primitive, ScopeVars, StackFrame
from ..base import Builtin

if TYPE_CHECKING:
    from ...engine import Engine

LOGGER = structlog.stdlib.get_logger(__name__)


class GameReset(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["game_reset"] = Primitive.block(
            operations=[Native(inst.game_reset)],
            name="game_reset",
            arg_names=["ticks_per_second"],
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def game_reset(self, frame: StackFrame) -> Primitive:
        ticks = frame.args.get("ticks_per_second", Primitive.of(None)).value
        self.engine.reset_game(ticks_per_sec=ticks)
        return Primitive.of(None)
