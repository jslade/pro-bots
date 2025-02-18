from typing import TYPE_CHECKING
from ...models.game.player import Player
from ...probotics.ops.all import Primitive, Native, ScopeVars, StackFrame

if TYPE_CHECKING:
    from .engine import Engine


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

        self._add_move(player, builtins)
        self._add_turn(player, builtins)

        return builtins

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
