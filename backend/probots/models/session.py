from datetime import datetime
from enum import Enum
from typing import Optional

from dataclasses import dataclass

from .user import User
from .websocket import WebSocket


class SessionType(str, Enum):
    SERVER = "srv"
    USER = "user"
    WATCHER = "watch"


@dataclass
class Session:
    type: SessionType
    id: str
    created_at: Optional[datetime] = None

    # Connection info
    ws: Optional[WebSocket] = None
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None

    user: Optional[User] = None

    @classmethod
    def type_from_id(cls, session_id: str) -> SessionType:
        match session_id[0]:
            case "s":
                return SessionType.SERVER
            case "u":
                return SessionType.USER
            case "w":
                return SessionType.WATCHER
            case _:
                raise ValueError(f"Invalid session ID format: {session_id}")
