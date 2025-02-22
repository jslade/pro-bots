from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

import structlog

from ....models.game.player import Player
from ....probotics.ops.all import Primitive, ScopeVars
from ....utils.callback_dict import CallbackDict
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class Me(Builtin):
    """The "me" builtin acts like a dictionary, providing information about the
    player and probot from the perspective of the player's code.

    It uses an actual dict() instance as a Primitive, but all of the data is
    determined via callbacks, so it is always up-to-date with the current state.
    """

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        me = cls(player, engine)
        builtins["me"] = Primitive.of(me.data)

    def __init__(self, player: Player, engine: "Engine") -> None:
        super().__init__(player, engine)

        self.data = CallbackDict(
            on_get=self.on_get,
            on_set=self.on_set,
            on_delete=self.on_delete,
        )

    GET = {
        "name": lambda me: me.player.name,
        "score": lambda me: me.player.score,
        "state": lambda me: enum_string(me.engine.probot_for_player(me.player).state),
        "x": lambda me: me.engine.probot_for_player(me.player).x,
        "y": lambda me: me.engine.probot_for_player(me.player).y,
        "orientation": lambda me: me.engine.probot_for_player(me.player).orientation,
        "energy": lambda me: me.engine.probot_for_player(me.player).energy,
        "crystals": lambda me: me.engine.probot_for_player(me.player).crystals,
        "globals": lambda me: me.get_globals(),
    }

    def on_get(self, key: str, default: Optional[Any] = None) -> Optional[Primitive]:
        LOGGER.info("me.get", player=self.player.name, key=key)

        try:
            return self.data.get_(key)
        except KeyError:
            if handler := self.GET.get(key, None):
                return Primitive.of(handler(self))
        return Primitive.of(default)

    def on_set(self, key: str, value: Any) -> None:
        LOGGER.info("me.set", player=self.player.name, key=key)

        raise KeyError(f"Not settable: {key}")

    def on_delete(self, key: str) -> None:
        raise KeyError(f"Not deletable: {key}")

    def get_globals(self) -> list[str]:
        globals = self.engine.programming.get_player_globals(self.player)
        return sorted(globals.keys())


def enum_string(enum_value: Enum) -> str:
    try:
        return enum_value.value
    except AttributeError:
        return str(enum_value)
