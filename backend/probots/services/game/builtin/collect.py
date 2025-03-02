from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Collect(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["collect"] = Primitive.block(
            operations=[Native(inst.collect)], name="collect", arg_names=[]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def collect(self, frame: StackFrame) -> Primitive:
        bonus = 200

        probot = self.engine.probot_for_player(self.player)
        collected = self.engine.energy.collect_crystals(probot, bonus=bonus)
        return Primitive.of(collected)
