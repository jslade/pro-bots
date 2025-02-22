from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

import structlog

from ....models.game.player import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from ...message_handlers.terminal_handler import TerminalOutput
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Print(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_print(frame: StackFrame, player=player) -> Optional[Primitive]:
            msg = frame.get("what")
            LOGGER.info("do_print", player=player, what=msg)
            engine.send_to_player(
                player,
                "terminal",
                "output",
                TerminalOutput(output=Primitive.output(msg)).as_msg(),
            )
            return None

        builtins["print"] = Primitive.block(
            operations=[Native(do_print)], name="print", arg_names=["what"]
        )
