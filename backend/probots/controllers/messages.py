import structlog

from ..app import SOCK

from ..models.message import Message
from ..models.session import Session
from ..models.websocket import WebSocket
from ..services.dispatcher import DISPATCHER
from ..services.session_service import SessionService, SESSIONS

LOGGER = structlog.get_logger(__name__)


@SOCK.route("/")
def handle_ws(ws: WebSocket):
    LOGGER.info("Websocket connection established")

    # Read the first messsage, should be a connection request
    try:
        data: str = ws.receive()
        message = Message.from_json(data)

        # Add a session and associated it with this websocket.
        # If the session already exists, it will be reused.
        session = SESSIONS.add_session(message.session_id)
        session.ws = ws
    except Exception as e:
        LOGGER.error("Failed to parse connection request", error=e)
        return

    LOGGER.info("Connection request received", session=session.id)
    DISPATCHER.send(session, "connection", "accepted", {})

    # Add session to dispatcher
    DISPATCHER.add_connection(session, ws)

    # Handle incoming, dispatcher will route to the correct service
    # and also handle sending any outgoing messages
    try:
        while True:
            try:
                data: str = ws.receive()
                message = Message.from_json(data)
            except Exception as e:
                if "Connection close" in str(e):
                    break

                LOGGER.error("Failed to parse message", error=e)
                break

            DISPATCHER.receive(session, message)
    finally:
        LOGGER.info("Websocket connection closed", session=session.id)
        DISPATCHER.remove_connection(session, ws)
        session.ws = None
