from typing import TYPE_CHECKING

import structlog

from ...models.game.player import Player
from ...probotics.ops.all import ScopeVars, Native, Primitive, StackFrame
from .builtin.all import (
    Builtin,
    Collect,
    Give,
    Inspect,
    IsIdle,
    Me,
    Move,
    NewList,
    NewObject,
    Print,
    Random,
    Say,
    ToInt,
    ToStr,
    Turn,
    Wait,
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
        NewList.add(player, self.engine, builtins)
        NewObject.add(player, self.engine, builtins)
        Random.add(player, self.engine, builtins)
        ToInt.add(player, self.engine, builtins)
        ToStr.add(player, self.engine, builtins)

        # Game-specific built-ins
        Collect.add(player, self.engine, builtins)
        Give.add(player, self.engine, builtins)
        Inspect.add(player, self.engine, builtins)
        IsIdle.add(player, self.engine, builtins)
        Me.add(player, self.engine, builtins)
        Move.add(player, self.engine, builtins)
        Print.add(player, self.engine, builtins)
        Say.add(player, self.engine, builtins)
        Turn.add(player, self.engine, builtins)
        Wait.add(player, self.engine, builtins)

        # A command to list all the built-ins
        Builtins.add(player, self.engine, builtins)

        return builtins


class Builtins(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player, builtins)

        builtins["builtins"] = Primitive.block(
            operations=[Native(inst.list_all)], name="builtins", arg_names=[]
        )

        builtins["commands"] = builtins["builtins"]

    def __init__(self, engine: "Engine", player: Player, builtins: ScopeVars) -> None:
        self.engine = engine
        self.player = player
        self.builtins = builtins

    def list_all(self, frame: StackFrame) -> Primitive:
        names = sorted(self.builtins.keys())
        return Primitive.of([Primitive.of(n) for n in names])
