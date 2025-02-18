from .connection_handler import ConnectionHandler
from .game_handler import GameHandler
from .manual_control_handler import ManualControlHandler
from .terminal_handler import TerminalHandler
from .user_handler import UserHandler

MESSAGE_HANDLERS = [
    ConnectionHandler(),
    GameHandler(),
    ManualControlHandler(),
    TerminalHandler(),
    UserHandler(),
]
