from typing import TYPE_CHECKING

import structlog

from .....app import APP
from .....db import DB
from .....models.all import User
from .....models.game.all import Player
from .....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from ..base import Builtin

if TYPE_CHECKING:
    from ...engine import Engine

LOGGER = structlog.stdlib.get_logger(__name__)


class Password(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["password"] = Primitive.block(
            operations=[Native(inst.set_password)],
            name="password",
            arg_names=["name", "password"],
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def set_password(self, frame: StackFrame) -> Primitive:
        name = frame.get("name")
        password = frame.get("password")

        assert name is not None and name.is_str, "name must be a string"
        assert password is not None and password.is_str, "password must be a string"

        with APP.app_context():
            user = User.with_name(name.value)
            if user:
                user.access_code = password.value
                DB.session.commit()

        return Primitive.of(None)
