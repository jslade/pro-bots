from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Give(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["give"] = Primitive.block(
            operations=[Native(inst.give)], name="give", arg_names=["amount", "to_whom"]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def give(self, frame: StackFrame) -> Primitive:
        amount = frame.get("amount")
        to_whom = frame.get("to_whom")

        if amount is None or amount.is_null:
            raise ValueError("Amount to give must be specified")
        if to_whom is None or to_whom.is_null:
            raise ValueError("To whom must be specified")

        probot = self.engine.probot_for_player(self.player)

        gave = self.engine.giving.give(probot, amount.value, Primitive.output(to_whom))
        return Primitive.of(gave)
