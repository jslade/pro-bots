from .connection_handler import ConnectionHandler
from .terminal_handler import TerminalHandler

MESSAGE_HANDLERS = [
    ConnectionHandler(),
    TerminalHandler(),
]
