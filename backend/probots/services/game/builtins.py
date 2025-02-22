from typing import TYPE_CHECKING

import structlog

from ...models.game.player import Player
from ...models.game.probot import ProbotState
from ...probotics.ops.all import Breakpoint, Native, Primitive, ScopeVars, StackFrame
from .builtin.all import IsIdle, Me, Move, Print, Turn, Wait

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

        IsIdle.add(player, self.engine, builtins)
        Move.add(player, self.engine, builtins)
        Turn.add(player, self.engine, builtins)
        Wait.add(player, self.engine, builtins)

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

    # TODO: needed? or maybe get_builtins() is enough?
    def update_builtins(self, player: Player) -> None:
        builtins = self.get_builtins(player)
        return builtins
