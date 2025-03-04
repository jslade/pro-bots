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

        probot_info = self.probot_info(cell_probot) if cell_probot else None

        result = {
            "x": Primitive.of(x),
            "y": Primitive.of(y),
            "crystals": Primitive.of(cell.crystals),
            "probot": Primitive.of(probot_info),
        }

        return Primitive.of(result)

    @classmethod
    def probot_info(cls, probot):
        return {
            "name": Primitive.of(probot.player.display_name),
            "state": Primitive.of(enum_string(probot.state)),
            "energy": Primitive.of(probot.energy),
            "crystals": Primitive.of(probot.crystals),
            "score": Primitive.of(probot.player.score),
            "x": Primitive.of(probot.x),
            "y": Primitive.of(probot.y),
            "orientation": Primitive.of(enum_string(probot.orientation)),
        }
