from .connection_handler import ConnectionHandler
from .manual_control_handler import ManualControlHandler
from .terminal_handler import TerminalHandler

MESSAGE_HANDLERS = [
    ConnectionHandler(),
    TerminalHandler(),
    ManualControlHandler(),
]
