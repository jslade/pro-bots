import random
from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Random(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["random"] = Primitive.block(
            operations=[Native(inst.random)], name="random", arg_names=["max"]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def random(self, frame: StackFrame) -> Primitive:
        max = frame.get("max")
        result = random.randint(0, max.value if max else 1)
        return Primitive.of(result)
