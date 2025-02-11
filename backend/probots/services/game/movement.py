from typing import TYPE_CHECKING

import structlog

from ...models.game.all import Probot, ProbotOrientation, ProbotState, Transition

if TYPE_CHECKING:
    from .engine import Engine

LOGGER = structlog.get_logger(__name__)


class IllegalMove(Exception):
    pass


class MovementService:
    """Handles all movement of the Probots
    - validating movement requests are legal
    - executing the movement, including the interstitial states"""

    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def move(self, probot: Probot, backward: bool = False) -> bool:
        """Initiate the move either forward or backward, one space"""
        # LOGGER.info("MOVE", probot=probot, backward=backward)

        #
        # Validate move
        #
        if probot.state != ProbotState.idle:
            return False

        x, y, orient = probot.position

        try:
            new_x, new_y = self.next_location(x, y, orient, -1 if backward else 1)
        except IllegalMove:
            return False

        speed_factor = 1.5 if backward else 1
        required_energy = int(100 * speed_factor)
        if probot.energy < required_energy:
            return False

        #
        # Execute move move
        #

        # Immediately mark the bot at the new location, to prevent
        # potential conflict of another bot moving to the same space
        probot.x = new_x
        probot.y = new_y

        # Create a transition to animate the moving state
        def start_move(transit):
            self.start_move(probot, transit, required_energy)

        def update_move(transit):
            self.update_move(probot, transit)

        def complete_move(transit):
            self.complete_move(probot, transit)

        transit = Transition(
            name="moving",
            total_steps=int(5 * speed_factor),
            initial=(x, y),
            final=(new_x, new_y),
            on_start=start_move,
            on_update=update_move,
            on_complete=complete_move,
        )
        self.engine.transitioner.add(transit)

    def next_location(
        self, x: int, y: int, orient: ProbotOrientation, delta: int
    ) -> tuple[int, int]:
        match orient:
            case ProbotOrientation.N:
                y -= delta
            case ProbotOrientation.S:
                y += delta
            case ProbotOrientation.E:
                x += delta
            case ProbotOrientation.W:
                x -= delta

        if x < 0 or x >= self.engine.grid.width or y < 0 or y >= self.engine.grid.height:
            raise IllegalMove

        if not self.engine.is_empty_cell(x, y):
            raise IllegalMove

        return (x, y)

    TURN_FROM_TO = {
        (ProbotOrientation.N, "left"): ProbotOrientation.W,
        (ProbotOrientation.N, "right"): ProbotOrientation.E,
        (ProbotOrientation.S, "left"): ProbotOrientation.E,
        (ProbotOrientation.S, "right"): ProbotOrientation.W,
        (ProbotOrientation.E, "left"): ProbotOrientation.N,
        (ProbotOrientation.E, "right"): ProbotOrientation.S,
        (ProbotOrientation.W, "left"): ProbotOrientation.S,
        (ProbotOrientation.W, "right"): ProbotOrientation.N,
    }

    def start_move(
        self, probot: Probot, transit: Transition, required_energy: int
    ) -> None:
        probot.state = ProbotState.moving
        probot.energy -= required_energy

        self.engine.notify_of_probot_change(probot)

    def update_move(self, probot: Probot, transit: Transition) -> None:
        dtick = 1.0 / transit.total_steps

        match probot.orientation:
            case ProbotOrientation.N:
                probot.dy += dtick
            case ProbotOrientation.S:
                probot.dy -= dtick
            case ProbotOrientation.E:
                probot.dx += dtick
            case ProbotOrientation.W:
                probot.dx -= dtick

        self.engine.notify_of_probot_change(probot)

    def complete_move(self, probot: Probot, transit: Transition) -> None:
        probot.state = ProbotState.idle
        probot.dx = 0
        probot.dy = 0

        self.engine.notify_of_probot_change(probot)

    def turn(self, probot: Probot, dir: str) -> bool:
        """Just rotating in place"""
        # LOGGER.info("TURN", probot=probot, dir=dir)

        #
        # Validate move
        #
        if probot.state != ProbotState.idle:
            return False

        orient = probot.orientation
        key = (orient, dir)
        new_orient = self.TURN_FROM_TO.get(key, None)
        if not new_orient:
            return False

        required_energy = 10
        if probot.energy < required_energy:
            return False

        #
        # Execute move move
        #

        # Create a transition to animate the moving state
        def start_turn(transit):
            self.start_turn(probot, transit, required_energy)

        def update_turn(transit):
            self.update_turn(probot, transit, dir)

        def complete_turn(transit):
            self.complete_turn(probot, transit, new_orient)

        transit = Transition(
            name="turning",
            total_steps=5,
            initial=orient,
            final=new_orient,
            on_start=start_turn,
            on_update=update_turn,
            on_complete=complete_turn,
        )
        self.engine.transitioner.add(transit)

    def start_turn(
        self, probot: Probot, transit: Transition, required_energy: int
    ) -> None:
        probot.state = ProbotState.turning
        probot.energy -= required_energy

        self.engine.notify_of_probot_change(probot)

    def update_turn(self, probot: Probot, transit: Transition, dir: str) -> None:
        dtick = 90.0 / transit.total_steps
        if dir == "left":
            probot.dorient += dtick
        else:
            probot.dorient -= dtick

        self.engine.notify_of_probot_change(probot)

    def complete_turn(
        self, probot: Probot, transit: Transition, new_orient: ProbotOrientation
    ) -> None:
        probot.state = ProbotState.idle
        probot.orientation = new_orient
        probot.dorient = 0

        self.engine.notify_of_probot_change(probot)
