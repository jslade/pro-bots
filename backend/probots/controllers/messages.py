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

        session = SESSIONS.add_session(message.session_id)
        session.ws = ws
    except Exception as e:
        LOGGER.error("Failed to parse connection request", error=e)
        return

    LOGGER.info("Connection request received", session=session.id)
    connection_response = Message(
        type="connection",
        event="accepted",
        session_id=session.id,
        data={},
    )
    ws.send(connection_response.model_dump_json())

    # Add session to dispatcher
    DISPATCHER.add_session(session, ws)

    # Handle incoming, outgoing messages
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

            DISPATCHER.receive(message, session)
    finally:
        LOGGER.info("Websocket connection closed", session=session.id)
        SESSIONS.remove_session(session)
