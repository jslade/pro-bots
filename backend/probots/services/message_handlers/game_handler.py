import structlog

from ...models.all import BaseSchema, Message, Session
from ...models.game.all import Player, ProbotOrientation
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class AddPlayerRequest(BaseSchema):
    session_id: str


class GameHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("game", "get_current", self.current_state)
        dispatcher.register_handler("game", "add_player", self.add_player)

    def current_state(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        ENGINE.notify_of_current_state(session)

    def add_player(
        self, session: Session, message: Message, dipatcher: Dispatcher
    ) -> None:
        player = ENGINE.player_for_user(session.user)
        if not player:
            if not session.user:
                LOGGER.warning("Can't add player for session without user")
                return

            player = Player(
                name=session.user.name,
                colors=ENGINE.coloring.generate_random(theme="dark"),
                session_id=session.id,
            )
            ENGINE.add_player(player, session=session)
            ENGINE.spawn_probot(player)
        else:
            player.session_id = session.id

        ENGINE.notify_of_current_state(session)
