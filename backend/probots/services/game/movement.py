import math
from enum import Enum
from typing import TYPE_CHECKING

import structlog

from ...models.game.all import Probot, ProbotOrientation, ProbotState, Transition

if TYPE_CHECKING:
    from .engine import Engine

LOGGER = structlog.get_logger(__name__)


class IllegalMove(Exception):
    pass


class MovementDir(str, Enum):
    forward = "forward"
    backward = "backward"
    left = "left"
    right = "right"


RADS_90 = math.pi / 2.0
RADS_45 = math.pi / 4.0
RADS_5 = RADS_45 / 9


class MovementService:
    """Handles all movement of the Probots
    - validating movement requests are legal
    - executing the movement, including the interstitial states"""

    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def move(
        self, probot: Probot, dir: MovementDir = MovementDir.forward, bonus: int = 0
    ) -> bool:
        """Initiate the move by one space"""
        # LOGGER.info("MOVE", probot=probot, dir=dir)

        #
        # Validate move
        #
        if probot.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            self.engine.send_output_to_player(
                probot.player, f"move: probot not idle ({probot.state})"
            )
            return False

        x, y, orient = probot.position

        try:
            new_x, new_y = self.next_location(x, y, orient, dir)
        except IllegalMove:
            self.engine.send_output_to_player(probot.player, "move: can't move there")
            return False

        speed_factor = 1
        match dir:
            case MovementDir.left:
                speed_factor = 1.5
            case MovementDir.right:
                speed_factor = 1.5
            case MovementDir.backward:
                speed_factor = 2.5

        required_energy = int(50 * speed_factor)
        if probot.energy < required_energy:
            self.engine.update_score(probot.player, -5)
            self.engine.send_output_to_player(probot.player, "move: not enough energy")
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
            self.start_move(probot, transit, dir, required_energy)

        def update_move(transit):
            self.update_move(probot, transit, dir)

        def complete_move(transit):
            self.complete_move(probot, transit, bonus)

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

        return True

    def next_location(
        self, x: int, y: int, orient: ProbotOrientation, dir: MovementDir
    ) -> tuple[int, int]:
        match orient:
            case ProbotOrientation.N:
                match dir:
                    case MovementDir.forward:
                        y += 1
                    case MovementDir.backward:
                        y -= 1
                    case MovementDir.left:
                        x -= 1
                    case MovementDir.right:
                        x += 1
            case ProbotOrientation.S:
                match dir:
                    case MovementDir.forward:
                        y -= 1
                    case MovementDir.backward:
                        y += 1
                    case MovementDir.left:
                        x += 1
                    case MovementDir.right:
                        x -= 1
            case ProbotOrientation.E:
                match dir:
                    case MovementDir.forward:
                        x += 1
                    case MovementDir.backward:
                        x -= 1
                    case MovementDir.left:
                        y += 1
                    case MovementDir.right:
                        y -= 1
            case ProbotOrientation.W:
                match dir:
                    case MovementDir.forward:
                        x -= 1
                    case MovementDir.backward:
                        x += 1
                    case MovementDir.left:
                        y -= 1
                    case MovementDir.right:
                        y += 1

        if x < 0 or x >= self.engine.grid.width or y < 0 or y >= self.engine.grid.height:
            raise IllegalMove

        if not self.engine.is_empty_cell(x, y):
            raise IllegalMove

        return (x, y)

    def start_move(
        self, probot: Probot, transit: Transition, dir: MovementDir, required_energy: int
    ) -> None:
        probot.state = ProbotState.moving
        probot.energy -= required_energy

        match probot.orientation:
            case ProbotOrientation.N:
                match dir:
                    case MovementDir.forward:
                        probot.dy = -1.0
                    case MovementDir.backward:
                        probot.dy = 1.0
                    case MovementDir.left:
                        probot.dx = 1.0
                        probot.dorient = RADS_5
                    case MovementDir.right:
                        probot.dx = -1.0
                        probot.dorient = -RADS_5
            case ProbotOrientation.S:
                match dir:
                    case MovementDir.forward:
                        probot.dy = 1.0
                    case MovementDir.backward:
                        probot.dy = -1.0
                    case MovementDir.left:
                        probot.dx = -1.0
                        probot.dorient = RADS_5
                    case MovementDir.right:
                        probot.dx = 1.0
                        probot.dorient = -RADS_5
            case ProbotOrientation.E:
                match dir:
                    case MovementDir.forward:
                        probot.dx = -1.0
                    case MovementDir.backward:
                        probot.dx = 1.0
                    case MovementDir.left:
                        probot.dy = -1.0
                        probot.dorient = RADS_5
                    case MovementDir.right:
                        probot.dy = 1.0
                        probot.dorient = -RADS_5
            case ProbotOrientation.W:
                match dir:
                    case MovementDir.forward:
                        probot.dx = 1.0
                    case MovementDir.backward:
                        probot.dx = -1.0
                    case MovementDir.left:
                        probot.dy = 1.0
                        probot.dorient = RADS_5
                    case MovementDir.right:
                        probot.dy = -1.0
                        probot.dorient = -RADS_5

        self.engine.programming.suspend_player(probot.player)
        self.engine.notify_of_probot_change(probot)

    def update_move(self, probot: Probot, transit: Transition, dir: MovementDir) -> None:
        dtick = 1.0 / transit.total_steps

        match probot.orientation:
            case ProbotOrientation.N:
                match dir:
                    case MovementDir.forward:
                        probot.dy += dtick
                    case MovementDir.backward:
                        probot.dy -= dtick
                    case MovementDir.left:
                        probot.dx -= dtick
                    case MovementDir.right:
                        probot.dx += dtick
            case ProbotOrientation.S:
                match dir:
                    case MovementDir.forward:
                        probot.dy -= dtick
                    case MovementDir.backward:
                        probot.dy += dtick
                    case MovementDir.left:
                        probot.dx += dtick
                    case MovementDir.right:
                        probot.dx -= dtick
            case ProbotOrientation.E:
                match dir:
                    case MovementDir.forward:
                        probot.dx += dtick
                    case MovementDir.backward:
                        probot.dx -= dtick
                    case MovementDir.left:
                        probot.dy += dtick
                    case MovementDir.right:
                        probot.dy -= dtick
            case ProbotOrientation.W:
                match dir:
                    case MovementDir.forward:
                        probot.dx -= dtick
                    case MovementDir.backward:
                        probot.dx += dtick
                    case MovementDir.left:
                        probot.dy -= dtick
                    case MovementDir.right:
                        probot.dy += dtick

        self.engine.notify_of_probot_change(probot)

    def complete_move(self, probot: Probot, transit: Transition, bonus: int = 0) -> None:
        probot.dx = 0
        probot.dy = 0
        probot.dorient = 0

        self.engine.probot_idle(probot)
        self.engine.update_score(probot.player, 1 + bonus)

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

    def turn(self, probot: Probot, dir: str, bonus: int = 0) -> bool:
        """Just rotating in place"""
        # LOGGER.info("TURN", probot=probot, dir=dir)

        match dir.lower():
            case "l":
                dir = "left"
            case "r":
                dir = "right"

        #
        # Validate turn
        #
        if probot.state != ProbotState.idle:
            self.engine.update_score(probot.player, -10)
            self.engine.send_output_to_player(
                probot.player, f"turn: probot not idle ({probot.state})"
            )
            return False

        orient = probot.orientation
        key = (orient, dir)
        new_orient = self.TURN_FROM_TO.get(key, None)
        if not new_orient:
            self.engine.send_output_to_player(probot.player, "turn: illegal turn")
            return False

        required_energy = 10
        if probot.energy < required_energy:
            self.engine.update_score(probot.player, -5)
            self.engine.send_output_to_player(probot.player, "turn: not enough energy")
            return False

        #
        # Execute turn
        #

        # Create a transition to animate the moving state
        def start_turn(transit):
            self.start_turn(probot, transit, required_energy)

        def update_turn(transit):
            self.update_turn(probot, transit, dir)

        def complete_turn(transit):
            self.complete_turn(probot, transit, new_orient, bonus=bonus)

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

        return True

    def start_turn(
        self, probot: Probot, transit: Transition, required_energy: int
    ) -> None:
        probot.state = ProbotState.turning
        probot.energy -= required_energy

        self.engine.notify_of_probot_change(probot)
        self.engine.programming.suspend_player(probot.player)

    def update_turn(self, probot: Probot, transit: Transition, dir: str) -> None:
        dtick = RADS_90 / transit.total_steps
        if dir == "left":
            probot.dorient += dtick
        else:
            probot.dorient -= dtick

        self.engine.notify_of_probot_change(probot)

    def complete_turn(
        self,
        probot: Probot,
        transit: Transition,
        new_orient: ProbotOrientation,
        bonus: int = 0,
    ) -> None:
        probot.orientation = new_orient
        probot.dorient = 0

        self.engine.probot_idle(probot)
        self.engine.update_score(probot.player, 1 + bonus)
