from typing import TYPE_CHECKING, Optional

import structlog

from ...models.game.all import Player, Probot, Transition

if TYPE_CHECKING:
    from .engine import Engine

LOGGER = structlog.get_logger(__name__)


class TransitionService:
    """Handles updates to transitions (animations)"""

    def __init__(self, engine: "Engine") -> None:
        self.engine = engine
        self.transitions = []

    def add(
        self,
        transit: Transition,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> None:
        self.transitions.append(transit)

        def start():
            return self.start(transit, probot=probot, player=player)

        self.engine.add_game_work(
            start,
            probot=probot,
            player=player,
        )

    def start(
        self,
        transit: Transition,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> None:
        if transit.on_start:
            try:
                transit.on_start(transit)
            except Exception:
                self.transitions.remove(transit)
                pass

        self.schedule_remaining(transit, probot=probot, player=player)

    def update(
        self,
        transit: Transition,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> None:
        if transit.on_update:
            try:
                transit.on_update(transit)
            except Exception:
                self.transitions.remove(transit)
                pass

        if transit.progress < transit.total_steps:
            transit.progress += 1

        self.schedule_remaining(transit, probot=probot, player=player)

    def complete(
        self,
        transit: Transition,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> None:
        try:
            self.transitions.remove(transit)
        except ValueError:
            pass

        if transit.on_complete:
            transit.on_complete(transit)

    def schedule_remaining(
        self,
        transit: Transition,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> None:
        if transit.progress < transit.total_steps:

            def update():
                return self.update(transit, probot=probot, player=player)

            self.engine.add_game_work(
                update,
                probot=probot,
                player=player,
            )
        else:

            def complete():
                return self.complete(transit, probot=probot, player=player)

            self.engine.add_game_work(
                complete,
                probot=probot,
                player=player,
            )
