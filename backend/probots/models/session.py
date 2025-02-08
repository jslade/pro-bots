from datetime import datetime
from enum import Enum
from typing import Optional

from dataclasses import dataclass

from .user import User
from .websocket import WebSocket


class SessionType(str, Enum):
    USER = "user"
    SERVER = "srv"


@dataclass
class UserInfo:
    user: User
    display_name: str


@dataclass
class Session:
    type: SessionType
    id: str
    created_at: Optional[datetime] = None

    # Connection info
    ws: Optional[WebSocket] = None
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None

    user: Optional[UserInfo] = None

    @classmethod
    def type_from_id(cls, session_id: str) -> SessionType:
        match session_id[0]:
            case "u":
                return SessionType.USER
            case "s":
                return SessionType.SERVER
            case _:
                raise ValueError(f"Invalid session ID format: {session_id}")
