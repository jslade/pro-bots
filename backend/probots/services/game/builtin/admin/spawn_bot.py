from typing import TYPE_CHECKING

import structlog

from .....app import APP
from .....models.all import Program, User
from .....models.game.all import Player, Probot
from .....probotics.ops.all import Native, Operation, Primitive, ScopeVars, StackFrame
from ..base import Builtin

if TYPE_CHECKING:
    from ...engine import Engine

LOGGER = structlog.stdlib.get_logger(__name__)


class SpawnBot(Builtin):
    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["spawn_bot"] = Primitive.block(
            operations=[Native(inst.spawn_bot)],
            name="spawn_bot",
            arg_names=["name", "profile", "other"],
        )

    def __init__(self, engine: "Engine", player: Player) -> None:
        self.engine = engine
        self.player = player

    def spawn_bot(self, frame: StackFrame) -> Primitive:
        """Create a new player that runs as a bot"""
        name = frame.get("name")
        profile = frame.get("profile")
        other = frame.get("other")
        colors = frame.get("colors")

        assert name is not None and name.is_str, "name must be a string"
        assert profile is not None and profile.is_str, "profile must be a string"
        assert other is None or other.is_object, "other must be an object"

        if self.engine.get_player(name.value):
            raise ValueError(f"Player {name.value} already exists")

        ops = self.load_profile(profile.value)

        other_dict: ScopeVars = other.value if other else ScopeVars()

        if "colors" in other_dict:
            color_scheme = self.engine.coloring.generate_from_object(other_dict["colors"])
        else:
            color_scheme = self.engine.coloring.generate_random(theme="light")

        player = Player(
            name=name.value,
            display_name=name.value,
            colors=color_scheme,
            score=0,
        )
        self.engine.add_player(player, start_ops=ops)

        probot = self.engine.spawn_probot(player)

        return Primitive.of(None)

    def load_profile(self, profile: str) -> list[Operation]:
        """Load the profile for the bot"""
        LOGGER.info("Loading profile", profile=profile)

        with APP.app_context():
            user = User.with_name(profile)
            assert user is not None, f"User {profile} not found"
            program = user.current_program
            assert program is not None, f"User {profile} has no program"

        ops = self.engine.programming.compile(program.content)
        return ops
