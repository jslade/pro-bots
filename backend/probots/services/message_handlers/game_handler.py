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

            colors = ENGINE.coloring.generate_random(theme="dark")
            if session.user.color_body:
                colors.body = session.user.color_body
            if session.user.color_head:
                colors.head = session.user.color_head
            if session.user.color_tail:
                colors.tail = session.user.color_tail

            player = Player(
                name=session.user.name,
                display_name=session.user.display_name or session.user.name,
                colors=colors,
                session_id=session.id,
            )
            ENGINE.add_player(player, session=session)
            ENGINE.spawn_probot(player)
        else:
            player.session_id = session.id

        ENGINE.notify_of_current_state(session)
