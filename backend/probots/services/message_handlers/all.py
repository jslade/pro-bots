from .connection_handler import ConnectionHandler
from .game_handler import GameHandler
from .manual_control_handler import ManualControlHandler
from .terminal_handler import TerminalHandler

MESSAGE_HANDLERS = [
    ConnectionHandler(),
    GameHandler(),
    ManualControlHandler(),
    TerminalHandler(),
]
