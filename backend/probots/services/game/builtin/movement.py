from typing import TYPE_CHECKING

import structlog

from ....models.game.all import Player, ProbotState
from ....probotics.ops.all import Breakpoint, Native, Primitive, ScopeVars, StackFrame
from ..movement import MovementDir
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
        inst = cls(engine, player)

        builtins["move"] = Primitive.block(
            operations=[Native(inst.move)], name="move", arg_names=["dir"]
        )

        # For convenience:
        builtins["forward"] = Primitive.of("forward")
        builtins["backward"] = Primitive.of("backward")
        builtins["left"] = Primitive.of("left")
        builtins["right"] = Primitive.of("right")

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def move(self, frame: StackFrame) -> Primitive:
        dir = "forward"
        bonus = 5

        if frame.args:
            got = frame.args.get("dir", None)
            if got is not None and not got.is_null:
                dir = MovementDir(got.value)

                match dir:
                    case MovementDir.backward:
                        bonus = 20
                    case MovementDir.left:
                        bonus = 10
                    case MovementDir.right:
                        bonus = 10

        probot = self.engine.probot_for_player(self.player)
        self.engine.mover.move(probot, dir=dir, bonus=bonus)


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


class Wait(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["wait"] = Primitive.block(
            operations=[Native(inst.wait)], name="wait", arg_names=["ticks"]
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def wait(self, frame: StackFrame) -> Primitive:
        ticks = 1

        if frame.args:
            got = frame.args.get("ticks", None)
            if got is not None and not got.is_null:
                ticks = got.value

        # Raise a break exception and stop the interpreter on this context
        probot = self.engine.probot_for_player(self.player)
        self.engine.add_probot_work(probot, self.engine.ensure_not_stopped, delay=ticks)
        raise Breakpoint(reason="wait", stop=True)
