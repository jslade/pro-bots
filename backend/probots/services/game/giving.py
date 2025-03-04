from typing import TYPE_CHECKING

import structlog

from ...models.game.all import Probot, ProbotOrientation, ProbotState, Transition
from ...probotics.ops.all import Primitive

if TYPE_CHECKING:
    from .engine import Engine


LOGGER = structlog.get_logger(__name__)


class GivingService:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def give(self, probot: Probot, amount: int, to_whom: str) -> bool:
        """Initiate giving crystals to another probot"""
        # LOGGER.info("GIVE", probot=probot, amount=amount, to_whom=to_whom)

        #
        # Validate
        #
        if probot.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "give: probot not idle", probot=probot.player.name, state=probot.state
            )
            return False

        target_player = self.engine.get_player(to_whom)
        if not target_player:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "give: no target player", probot=probot.player.name, to_whom=to_whom
            )
            return False
        target = self.engine.probot_for_player(target_player)
        if not target:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "give: no target probot", probot=probot.player.name, to_whom=to_whom
            )
            return False

        if target.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            LOGGER.info(
                "give: target not idle", probot=probot.player.name, to_whom=to_whom
            )
            return False

        if target.crystals + amount > Probot.MAX_CRYSTALS:
            amount = Probot.MAX_CRYSTALS - target.crystals

        required_energy = 50
        if probot.energy < required_energy:
            self.engine.update_score(probot.player, -5)
            LOGGER.info("give: no energy", probot=probot.player.name)
            return False

        required_crystals = 10 + amount
        if probot.crystals < required_crystals:
            self.engine.update_score(probot.player, -5)
            LOGGER.info("give: no crystals", probot=probot.player.name)
            return False

        # Target must be in front of the probot, and facing
        if not self.is_in_front_and_facing(probot, target):
            self.engine.update_score(probot.player, -5)
            LOGGER.info(
                "give: not in front", probot=probot.player.name, target=target.player.name
            )
            return False

        #
        # Execute
        #

        bonus = 10_000

        # Create a transition to animate the moving state
        def start_giving(transit):
            self.start_giving(probot, target, transit, required_energy, required_crystals)

        def update_giving(transit):
            self.update_giving(probot, target, transit, required_crystals, amount)

        def complete_giving(transit):
            self.complete_giving(probot, target, transit, amount, bonus)

        transit = Transition(
            name="giving",
            total_steps=max(15, int(amount / 10)),
            initial=(probot.crystals, target.crystals),
            final=(probot.crystals - required_crystals, target.crystals + amount),
            on_start=start_giving,
            on_update=update_giving,
            on_complete=complete_giving,
        )
        self.engine.transitioner.add(transit)

        return True

    def is_in_front_and_facing(self, probot: Probot, target: Probot) -> bool:
        x, y, orientation = probot.position
        tx, ty, _ = target.position
        dx = tx - x
        dy = ty - y
        match orientation:
            case ProbotOrientation.N:
                return dx == 0 and dy == 1 and target.orientation == ProbotOrientation.S
            case ProbotOrientation.S:
                return dx == 0 and dy == -1 and target.orientation == ProbotOrientation.N
            case ProbotOrientation.E:
                return dx == 1 and dy == 0 and target.orientation == ProbotOrientation.W
            case ProbotOrientation.W:
                return dx == -1 and dy == 0 and target.orientation == ProbotOrientation.E

        return False

    def start_giving(
        self,
        probot: Probot,
        target: Probot,
        transit: Transition,
        required_energy: int,
        required_crystals: int,
    ) -> None:
        probot.state = ProbotState.giving
        target.state = ProbotState.receiving
        probot.energy -= required_energy
        probot.crystals -= required_crystals

        self.engine.notify_of_probot_change(probot)
        self.engine.notify_of_probot_change(target)
        self.engine.programming.suspend_player(probot.player)
        self.engine.programming.suspend_player(target.player)

    def update_giving(
        self,
        probot: Probot,
        target: Probot,
        transit: Transition,
        give_amount: int,
        receive_amount: int,
    ) -> None:
        delta_giver = int(1.0 * give_amount / transit.total_steps)
        probot.crystals -= delta_giver

        delta_receiver = int(1.0 * receive_amount / transit.total_steps)
        target.crystals += delta_receiver

        self.engine.notify_of_probot_change(probot)
        self.engine.notify_of_probot_change(target)

    def complete_giving(
        self,
        probot: Probot,
        target: Probot,
        transit: Transition,
        amount: int,
        bonus: int = 0,
    ) -> None:
        probot.crystals = transit.final[0]
        if probot.crystals < 0:
            probot.crystals = 0

        target.crystals = transit.final[1]
        if target.crystals > Probot.MAX_CRYSTALS:
            target.crystals = Probot.MAX_CRYSTALS

        self.engine.probot_idle(probot)
        self.engine.probot_idle(target)
        self.engine.update_score(probot.player, bonus)
        self.engine.update_score(target.player, bonus)

        self.engine.programming.emit_event(
            "on_received",
            player=target.player,
            args={
                "amount": Primitive.of(amount),
                "from_whom": Primitive.of(probot.player.display_name),
            },
        )

        self.engine.programming.emit_event(
            "on_gave",
            player=probot.player,
            args={
                "amount": Primitive.of(amount),
                "to_whom": Primitive.of(target.player.display_name),
            },
        )
