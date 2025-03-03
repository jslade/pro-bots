import math
from typing import TYPE_CHECKING

import structlog

from ...models.game.all import Cell, Probot, ProbotState, Transition
from ...models.game.probot import Probot, ProbotState
from ...probotics.ops.all import Primitive

if TYPE_CHECKING:
    from .engine import Engine


LOGGER = structlog.get_logger(__name__)


class EnergyService:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def collect_energy(self, probot: Probot) -> None:
        """Probots increase energy automatically, faster when idle, even faster when
        fueled up on crystals"""
        if probot.energy >= Probot.MAX_ENERGY:
            return

        rate = 50.0

        match probot.state:
            case ProbotState.idle:
                rate *= 0.4
            case ProbotState.moving:
                rate *= 0.01
            case ProbotState.turning:
                rate *= 0.02
            case ProbotState.jumping:
                rate = 0.0

        rate *= 1 + (0.04 * probot.crystals)

        pct = 1.0 * (probot.energy / Probot.MAX_ENERGY)
        delta_raw = rate * (1.0 - pct)
        if delta_raw <= 0:
            return

        delta = int(delta_raw) or 1
        probot.energy += delta
        if probot.energy > Probot.MAX_ENERGY:
            probot.energy = Probot.MAX_ENERGY

        self.consume_crystals(probot, rate, delta)

        self.engine.notify_of_probot_change(probot)

    def consume_crystals(self, probot: Probot, rate: float, delta: int) -> None:
        """Consume crystals to increase the energy rate"""
        probot.crystals -= int(delta / 3)
        if probot.crystals < 0:
            probot.crystals = 0

    def collect_crystals(self, probot: Probot, bonus: int = 0) -> bool:
        """Initiate collection of crystals"""
        # LOGGER.info("COLLECT", probot=probot, backward=backward)

        #
        # Validate
        #
        if probot.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            return False

        x, y, _ = probot.position
        cell, _ = self.engine.get_cell(x, y)

        if cell.crystals <= 0:
            return False
        if probot.crystals >= Probot.MAX_CRYSTALS:
            return False

        # Time and energy required inverse proportional to the number of crystals
        # in the cell
        speed_factor = 1 + 3 * (1.0 - (1.0 * cell.crystals / Cell.MAX_CRYSTALS))
        required_energy = int(100 * speed_factor)
        if probot.energy < required_energy:
            self.engine.update_score(probot.player, -5)
            return False

        per_collection = 200
        if per_collection > cell.crystals:
            per_collection = cell.crystals
        if probot.crystals + per_collection > Probot.MAX_CRYSTALS:
            per_collection = Probot.MAX_CRYSTALS - probot.crystals

        #
        # Execute
        #

        # Create a transition to animate the moving state
        def start_collection(transit):
            self.start_collection(probot, transit, required_energy)

        def update_collection(transit):
            self.update_collection(probot, transit, per_collection)

        def complete_collection(transit):
            self.complete_collection(probot, transit, bonus)

        transit = Transition(
            name="collecting",
            total_steps=int(20 * speed_factor),
            initial=probot.crystals,
            final=probot.crystals + per_collection,
            on_start=start_collection,
            on_update=update_collection,
            on_complete=complete_collection,
        )
        self.engine.transitioner.add(transit)

        return True

    def start_collection(
        self, probot: Probot, transit: Transition, required_energy: int
    ) -> None:
        probot.state = ProbotState.collecting
        probot.energy -= required_energy

        self.engine.notify_of_probot_change(probot)
        self.engine.programming.suspend_player(probot.player)

    def update_collection(self, probot: Probot, transit: Transition, total: int) -> None:
        delta = int(1.0 * total / transit.total_steps)
        probot.crystals += delta

        self.engine.notify_of_probot_change(probot)

    def complete_collection(
        self, probot: Probot, transit: Transition, bonus: int = 0
    ) -> None:
        probot.crystals = transit.final

        self.engine.probot_idle(probot)
        self.engine.update_score(probot.player, bonus)

        # Just for testing:
        self.engine.programming.emit_event(
            "on_collected",
            player=probot.player,
            args={
                "crystals": Primitive.of(probot.crystals),
            },
        )
