from enum import Enum
from typing import Optional

from dataclasses import dataclass

from .websocket import WebSocket


class SessionType(str, Enum):
    USER = "user"
    SERVER = "srv"


@dataclass
class Session:
    type: SessionType
    id: str
    ws: Optional[WebSocket] = None

    @classmethod
    def type_from_id(cls, session_id: str) -> SessionType:
        match session_id[0]:
            case "u":
                return SessionType.USER
            case "s":
                return SessionType.SERVER
            case _:
                raise ValueError(f"Invalid session ID format: {session_id}")
