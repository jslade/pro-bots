from typing import TYPE_CHECKING

from ...models.game.probot import Probot, ProbotState

if TYPE_CHECKING:
    from .engine import Engine


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
        probot.crystals -= delta
        if probot.crystals < 0:
            probot.crystals = 0
