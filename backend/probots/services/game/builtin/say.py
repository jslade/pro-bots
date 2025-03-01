from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Say(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["say"] = Primitive.block(
            operations=[Native(inst.say)], name="say", arg_names=["what", "to_whom"]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def say(self, frame: StackFrame) -> Primitive:
        what = frame.get("what")
        to_whom = frame.get("to_whom")

        if what is None or what.is_null:
            raise ValueError("What to say must be specified")
        if to_whom is None or to_whom.is_null:
            raise ValueError("To whom must be specified")

        probot = self.engine.probot_for_player(self.player)

        said = self.engine.saying.say(
            probot, Primitive.output(what.value), Primitive.output(to_whom.value)
        )
        if not said:
            raise ValueError("Failed to send message")
