import queue
from typing import Optional
import structlog

from ...models.all import Message
from .map_maker import MapMaker

LOGGER = structlog.get_logger(__name__)


class Engine:
    """The game engine runs as a separate thread(s) from the main
    application.
    """

    def __init__(self) -> None:
        self.shutdown = False
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()

    def run(self) -> None:
        """This is the entrypoint for the main game thread. It should never exit
        until the process is being shutdown"""
        LOGGER.info("Game thread started")

        self.reset()

        while not self.shutdown:
            # Process any incoming messages
            try:
                received: Message = self.incoming.get(block=False, timeout=5)
                self.process_incoming(received)
            except queue.Empty:
                # Nothing in the queue... just iterate the while loop,
                # checking the shutdown condition
                pass

        LOGGER.info("Game thread terminating")

    def process_incoming(received):
        pass

    def reset(self) -> None:
        LOGGER.info("Resetting game")

        mm = MapMaker()
        self.grid = mm.generate(10, 10)


ENGINE = Engine()
