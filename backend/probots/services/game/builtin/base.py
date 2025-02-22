from typing import TYPE_CHECKING

from ....models.game.player import Player

if TYPE_CHECKING:
    from ..engine import Engine


class Builtin:
    player: Player
    engine: "Engine"

    def __init__(self, player: Player, engine: "Engine") -> None:
        self.player = player
        self.engine = engine
