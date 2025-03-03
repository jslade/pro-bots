from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin
from .me import enum_string

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Inspect(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["inspect"] = Primitive.block(
            operations=[Native(inst.inspect)], name="inspect", arg_names=["x", "y"]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def inspect(self, frame: StackFrame) -> Primitive:
        bonus = 50

        x = frame.get("x")
        y = frame.get("y")

        if x is None or x.is_null:
            probot = self.engine.probot_for_player(self.player)
            x = Primitive.of(probot.x)
            y = Primitive.of(probot.y)

        elif x.is_str:
            player = self.engine.get_player(x.value)
            if player is None:
                raise ValueError(f"Player {x.value} not found")
            probot = self.engine.probot_for_player(player)
            x = Primitive.of(probot.x)
            y = Primitive.of(probot.y)

        result = self.engine.inspection.inspect(x.value, y.value)
        self.engine.update_score(self.player, bonus)

        return result
