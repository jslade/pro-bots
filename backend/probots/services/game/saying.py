from typing import TYPE_CHECKING

import structlog

from ...models.game.all import Probot, ProbotOrientation, ProbotState, Transition
from ...probotics.ops.all import Primitive

if TYPE_CHECKING:
    from .engine import Engine


LOGGER = structlog.get_logger(__name__)


class SayingService:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def say(self, probot: Probot, msg: str, to_whom: str) -> bool:
        """Initiate saying a message"""
        # LOGGER.info("SAY", probot=probot, msg=msg, to_whom=to_whom)

        #
        # Validate
        #
        if probot.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "say: probot not idle", probot=probot.player.name, state=probot.state
            )
            return False

        target_player = self.engine.get_player(to_whom)
        if not target_player:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "say: no target player", probot=probot.player.name, to_whom=to_whom
            )
            return False
        target = self.engine.probot_for_player(target_player)
        if not target:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "say: no target probot", probot=probot.player.name, to_whom=to_whom
            )
            return False

        required_energy = 10
        if probot.energy < required_energy:
            self.engine.update_score(probot.player, -5)
            LOGGER.info("say: no energy", probot=probot.player.name)
            return False

        # Target must be in front of the probot, though not necessarily facing
        if not self.is_in_front(probot, target):
            self.engine.update_score(probot.player, -5)
            LOGGER.info(
                "say: not in front", probot=probot.player.name, target=target.player.name
            )
            return False

        #
        # Execute
        #

        bonus = 1_000

        # Create a transition to animate the moving state
        def start_saying(transit):
            self.start_saying(probot, transit, required_energy)

        def update_saying(transit):
            self.update_saying(probot, transit)

        def complete_saying(transit):
            self.complete_saying(probot, transit, target, bonus)

        transit = Transition(
            name="saying",
            total_steps=5,
            initial=probot.crystals,
            final=msg,
            on_start=start_saying,
            on_update=update_saying,
            on_complete=complete_saying,
        )
        self.engine.transitioner.add(transit)

        return True

    def is_in_front(self, probot: Probot, target: Probot) -> bool:
        x, y, orientation = probot.position
        tx, ty, _ = target.position
        dx = tx - x
        dy = ty - y
        match orientation:
            case ProbotOrientation.N:
                return dx == 0 and dy == 1
            case ProbotOrientation.S:
                return dx == 0 and dy == -1
            case ProbotOrientation.E:
                return dx == 1 and dy == 0
            case ProbotOrientation.W:
                return dx == -1 and dy == 0

        return False

    def start_saying(
        self, probot: Probot, transit: Transition, required_energy: int
    ) -> None:
        probot.state = ProbotState.saying
        probot.energy -= required_energy

        self.engine.notify_of_probot_change(probot)
        self.engine.programming.suspend_player(probot.player)

    def update_saying(self, probot: Probot, transit: Transition) -> None:
        dtick = 1.0 / transit.total_steps

        # self.engine.notify_of_probot_change(probot)

    def complete_saying(
        self, probot: Probot, transit: Transition, target: Probot, bonus: int = 0
    ) -> None:
        self.engine.probot_idle(probot)
        self.engine.update_score(probot.player, bonus)

        msg = transit.final
        self.engine.programming.emit_event(
            "on_message",
            player=target.player,
            args={
                "what": Primitive.of(msg),
                "from_whom": Primitive.of(probot.player.display_name),
            },
        )

        self.engine.programming.emit_event(
            "on_said",
            player=probot.player,
            args={
                "what": Primitive.of(msg),
                "to_whom": Primitive.of(target.player.display_name),
            },
        )
