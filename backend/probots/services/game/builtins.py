from typing import TYPE_CHECKING

import structlog

from ...models.game.player import Player
from ...models.game.probot import ProbotState
from ...probotics.ops.all import Breakpoint, Native, Primitive, ScopeVars, StackFrame
from .builtin.all import (
    Inspect,
    IsIdle,
    Me,
    Move,
    Print,
    Turn,
    Wait,
    ToInt,
    ToStr,
    NewList,
    NewObject,
)

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
        ToStr.add(player, self.engine, builtins)
        ToInt.add(player, self.engine, builtins)
        NewList.add(player, self.engine, builtins)
        NewObject.add(player, self.engine, builtins)

        # Game-specific built-ins
        Inspect.add(player, self.engine, builtins)
        IsIdle.add(player, self.engine, builtins)
        Me.add(player, self.engine, builtins)
        Move.add(player, self.engine, builtins)
        Print.add(player, self.engine, builtins)
        Turn.add(player, self.engine, builtins)
        Wait.add(player, self.engine, builtins)

        return builtins
