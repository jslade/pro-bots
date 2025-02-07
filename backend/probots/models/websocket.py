from typing import TYPE_CHECKING


class WebSocket:
    if TYPE_CHECKING:

        def send(self, message: str) -> None: ...
        def receive(self) -> str: ...
