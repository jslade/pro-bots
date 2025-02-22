from typing import TYPE_CHECKING

import structlog

from ...models.game.player import Player
from ...models.game.probot import ProbotState
from ...probotics.ops.all import Breakpoint, Native, Primitive, ScopeVars, StackFrame
from .builtin.all import Me, Print

if TYPE_CHECKING:
    from .engine import Engine


LOGGER = structlog.get_logger(__name__)


class BuiltinsService:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine
        self.builtins_per_player: dict[str, ScopeVars] = {}

    def get_builtins(self, player: Player) -> ScopeVars:
        if player.name not in self.builtins_per_player:
            self.builtins_per_player[player.name] = self.create_builtins(player)

        return self.builtins_per_player[player.name]

    def create_builtins(self, player: Player) -> ScopeVars:
        """Define a new set of built-ins bound to the player"""
        builtins: ScopeVars = {}

        # Basic language features
        self._add_list(builtins)
        self._add_object(builtins)

        # Game-specific built-ins
        Me.add(player, self.engine, builtins)
        Print.add(player, self.engine, builtins)

        self._add_is_idle(player, builtins)
        self._add_move(player, builtins)
        self._add_turn(player, builtins)
        self._add_wait(player, builtins)

        return builtins

    def _add_list(self, builtins: ScopeVars):
        def new_list(frame: StackFrame) -> Primitive:
            return Primitive.of([])

        builtins["list"] = Primitive.block(
            operations=[Native(new_list)], name="list", arg_names=[]
        )

    def _add_object(self, builtins: ScopeVars):
        def new_object(frame: StackFrame) -> Primitive:
            return Primitive.of({})

        builtins["object"] = Primitive.block(
            operations=[Native(new_object)], name="object", arg_names=[]
        )

    def _add_is_idle(self, player: Player, builtins: ScopeVars):
        def do_is_idle(frame: StackFrame) -> Primitive:
            probot = self.engine.probot_for_player(player)
            return Primitive.of(probot.state == ProbotState.idle)

        builtins["is_idle"] = Primitive.block(
            operations=[Native(do_is_idle)], name="is_idle", arg_names=[]
        )

    def _add_move(self, player: Player, builtins: ScopeVars):
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

            probot = self.engine.probot_for_player(player)
            self.engine.mover.move(probot, backward=backward, bonus=bonus)

        builtins["move"] = Primitive.block(
            operations=[Native(do_move)], name="move", arg_names=["dir"]
        )

        # For convenience:
        builtins["backward"] = Primitive.of("backward")

    def _add_turn(self, player: Player, builtins: ScopeVars):
        def do_turn(frame: StackFrame) -> Primitive:
            bonus = 3
            dir = frame.args["dir"]

            probot = self.engine.probot_for_player(player)
            self.engine.mover.turn(probot, dir=dir.value, bonus=bonus)

        builtins["turn"] = Primitive.block(
            operations=[Native(do_turn)], name="turn", arg_names=["dir"]
        )

        # For convenience:
        builtins["left"] = Primitive.of("left")
        builtins["right"] = Primitive.of("right")

    def _add_wait(self, player: Player, builtins: ScopeVars):
        def do_wait(frame: StackFrame) -> Primitive:
            # Raise a break exception and stop the interpreter on this context
            raise Breakpoint(reason="wait", stop=True)

        builtins["wait"] = Primitive.block(operations=[Native(do_wait)], name="wait")

    # TODO: needed? or maybe get_builtins() is enough?
    def update_builtins(self, player: Player) -> None:
        builtins = self.get_builtins(player)
        return builtins
