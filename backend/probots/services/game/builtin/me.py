from typing import TYPE_CHECKING, Any, Optional

import structlog

from ....models.game.player import Player
from ....probotics.ops.all import Primitive, ScopeVars
from ....utils.callback_dict import CallbackDict
from ..utils import enum_string
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
            on_iter=self.on_iter,
        )

    GET = {
        "name": lambda me: me.player.display_name,
        "score": lambda me: me.player.score,
        "state": lambda me: enum_string(me.engine.probot_for_player(me.player).state),
        "x": lambda me: me.engine.probot_for_player(me.player).x,
        "y": lambda me: me.engine.probot_for_player(me.player).y,
        "orientation": lambda me: enum_string(
            me.engine.probot_for_player(me.player).orientation
        ),
        "energy": lambda me: me.engine.probot_for_player(me.player).energy,
        "crystals": lambda me: me.engine.probot_for_player(me.player).crystals,
        "colors": lambda me: me.get_colors(),
        "globals": lambda me: me.get_globals(),
    }

    def on_iter(self) -> list[str]:
        return list(self.GET.keys())

    def on_get(self, key: str, default: Optional[Any] = None) -> Optional[Primitive]:
        try:
            return self.data.get_(key)
        except KeyError:
            if handler := self.GET.get(key, None):
                return Primitive.of(handler(self))
        return Primitive.of(default)

    def on_set(self, key: str, value: Primitive) -> None:
        if key == "name":
            self.player.display_name = str(value.value)
            self.engine.update_score(self.player, 5)
            self.engine.notify_of_player_change(self.player)

            if user := self.engine.user_for_player(self.player):
                user.display_name = self.player.display_name
            return

        raise KeyError(f"Not settable: {key}")

    def on_delete(self, key: str) -> None:
        raise KeyError(f"Not deletable: {key}")

    def get_globals(self) -> Primitive:
        globals = self.engine.programming.get_player_globals(self.player)
        return Primitive.of(globals)

    def get_colors(self) -> Primitive:
        color_dict = CallbackDict(
            on_get=self.on_get_color,
            on_set=self.on_set_color,
            on_delete=self.on_delete_color,
            on_iter=self.on_iter_color,
        )
        return Primitive.of(color_dict)

    def on_iter_color(self) -> list[str]:
        return ["head", "tail", "body"]

    def on_get_color(
        self, key: str, default: Optional[Any] = None
    ) -> Optional[Primitive]:
        if key == "head":
            return Primitive.of(self.player.colors.head)
        if key == "tail":
            return Primitive.of(self.player.colors.tail)
        if key == "body":
            return Primitive.of(self.player.colors.body)
        return Primitive.of(default)

    def on_set_color(self, key: str, value: Primitive) -> None:
        if key == "head":
            self.player.colors.head = str(value.value)
        elif key == "tail":
            self.player.colors.tail = str(value.value)
        elif key == "body":
            self.player.colors.body = str(value.value)
        else:
            raise KeyError(f"Not settable: {key}")

        if user := self.engine.user_for_player(self.player):
            user.color_head = self.player.colors.head
            user.color_tail = self.player.colors.tail
            user.color_body = self.player.colors.body

        self.engine.update_score(self.player, 5)
        self.engine.notify_of_player_change(self.player)
        self.engine.notify_of_probot_change(self.player)

    def on_delete_color(self, key: str) -> None:
        raise KeyError(f"Not deletable: {key}")
