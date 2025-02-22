from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player, ProbotState
from ....probotics.ops.all import Breakpoint, Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class IsIdle(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_is_idle(frame: StackFrame) -> Primitive:
            probot = engine.probot_for_player(player)
            return Primitive.of(probot.state == ProbotState.idle)

        builtins["is_idle"] = Primitive.block(
            operations=[Native(do_is_idle)], name="is_idle", arg_names=[]
        )


class Move(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_move(frame: StackFrame) -> Primitive:
            backward = False
            bonus = 5

            if frame.args:
                found = frame.args.get("dir", None)
                if found:
                    if found.value == "backward":
                        backward = True
                        bonus = 10
                    else:
                        raise ValueError("Invalid direction")

            probot = engine.probot_for_player(player)
            engine.mover.move(probot, backward=backward, bonus=bonus)

        builtins["move"] = Primitive.block(
            operations=[Native(do_move)], name="move", arg_names=["dir"]
        )

        # For convenience:
        builtins["backward"] = Primitive.of("backward")


class Turn(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_turn(frame: StackFrame) -> Primitive:
            bonus = 3
            dir = frame.args["dir"]

            probot = engine.probot_for_player(player)
            engine.mover.turn(probot, dir=dir.value, bonus=bonus)

        builtins["turn"] = Primitive.block(
            operations=[Native(do_turn)], name="turn", arg_names=["dir"]
        )

        # For convenience:
        builtins["left"] = Primitive.of("left")
        builtins["right"] = Primitive.of("right")


class Wait(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_wait(frame: StackFrame) -> Primitive:
            # Raise a break exception and stop the interpreter on this context
            raise Breakpoint(reason="wait", stop=True)

        builtins["wait"] = Primitive.block(operations=[Native(do_wait)], name="wait")
