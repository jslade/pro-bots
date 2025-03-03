from typing import TYPE_CHECKING

import structlog

from ...probotics.ops.all import Primitive
from .utils import enum_string

if TYPE_CHECKING:
    from .engine import Engine


LOGGER = structlog.get_logger(__name__)


class InspectionService:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine

    def inspect(self, x: int, y: int) -> Primitive:
        """Initiate saying a message"""
        # LOGGER.info("INSPECT", x=x, y=y)

        try:
            cell, cell_probot = self.engine.get_cell(x, y)
        except ValueError:
            return Primitive.of(None)

        probot_info = None
        if cell_probot:
            probot_info = {
                "name": Primitive.of(cell_probot.player.display_name),
                "state": Primitive.of(enum_string(cell_probot.state)),
                "energy": Primitive.of(cell_probot.energy),
                "crystals": Primitive.of(cell_probot.crystals),
                "score": Primitive.of(cell_probot.player.score),
                "x": Primitive.of(cell_probot.x),
                "y": Primitive.of(cell_probot.y),
                "orientation": Primitive.of(enum_string(cell_probot.orientation)),
            }

        result = {
            "x": Primitive.of(x),
            "y": Primitive.of(y),
            "crystals": Primitive.of(cell.crystals),
            "probot": Primitive.of(probot_info),
        }

        return Primitive.of(result)
