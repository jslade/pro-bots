from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

import structlog

from ....models.game.player import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from ...message_handlers.terminal_handler import TerminalOutput
from ..inspection import InspectionService
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Players(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["probots"] = Primitive.block(
            operations=[Native(inst.players)], name="probots", arg_names=[]
        )
        builtins["players"] = builtins["probots"]

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def players(self, frame: StackFrame) -> Primitive:
        probots = self.engine.probots
        probot_infos = [
            Primitive.of(InspectionService.probot_info(probot)) for probot in probots
        ]
        return Primitive.of(probot_infos)
