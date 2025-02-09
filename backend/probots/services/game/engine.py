import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

import structlog

from ...models.all import BaseSchema, Message
from ...models.game.all import Grid, Player, Probot
from ..dispatcher import DISPATCHER
from ..session_service import SESSIONS
from .map_maker import MapMaker

from .processor import Processor

LOGGER = structlog.get_logger(__name__)


class GameCurrentStateData(BaseSchema):
    grid: Grid
    players: list[Player]
    probots: list[Probot]


class GameResetData(BaseSchema):
    current: GameCurrentStateData


class Engine:
    """The game engine runs as a separate thread(s) from the main
    application.
    """

    def __init__(self) -> None:
        # Game communication / flow
        self.processor = Processor()
        self.incoming = self.processor.incoming
        self.outgoing = queue.Queue()
        self.stopped = False
        self.paused = False

        # Game entities
        self.grid: Grid = Grid.blank(1, 1)
        self.players: list[Player] = []
        self.probots: list[Probot] = []

    def run(self) -> None:
        """This is the entrypoint for the main game thread. It should never exit
        until the process is being shutdown"""
        LOGGER.info("Game thread started")

        # Start another thread for processing outbound messages
        self.outgoing_thread = threading.Thread(target=self.run_outgoing, daemon=True)
        self.outgoing_thread.start()

        # Start with a fresh initial game state
        self.processor.add_work(self.reset, critical=True)
        self.processor.add_work(self.report_ticks)

        # Frame rate of the simulation:
        self.processor.run()

    def run_outgoing(self) -> None:
        """This is the entrypoint for the "outgoing" game thread. It just waits
        for messages to be available on the outgoing queue and then sends them
        out via the dispatcher."""
        while not self.stopped:
            # Process any outgoing messages
            try:
                message: Message = self.outgoing.get(block=True, timeout=5)
                self.process_outgoing(message)
                self.outgoing.task_done()
            except queue.Empty:
                # Nothing in the queue... this timeout is really just here so
                # that another pass on the while condition (stopped) can be made
                pass

    def process_outgoing(self, message: Message):
        """Send out a message. This method is called in the context of the
        "main" thread, not the game thread, so it can directly use the
        main dispatcher"""
        if message.session_id:
            session = SESSIONS.get_session(message.session_id)
            if session:
                DISPATCHER.send(session, message.type, message.event, message.data)
        else:
            DISPATCHER.broadcast(message.type, message.event, message.data)

    def stop(self) -> None:
        LOGGER.info("Shutting down game")
        self.stopped = True
        self.processor.stop()

    def pause(self) -> None:
        if self.paused:
            return

        LOGGER.info("Game paused")
        self.paused = True
        self.processor.pause()

    def resume(self) -> None:
        if not self.paused:
            return

        LOGGER.info("Game resume")
        self.paused = False
        self.processor.resume()

    def reset(self) -> None:
        LOGGER.info("Resetting game")

        mm = MapMaker()
        self.grid = mm.generate(10, 10)

        # Tell everyone about the new game state
        game = GameResetData(
            current=GameCurrentStateData(
                grid=self.grid,
                players=[p for p in self.players],
                probots=[p for p in self.probots],
            )
        )

        message = Message(
            type="game",
            event="reset",
            session_id="",
            data=game.model_dump(),
        )
        self.outgoing.put(message)

    def report_ticks(self) -> None:
        LOGGER.info("ticks", ticks=self.processor.ticks)

        self.processor.add_work(self.report_ticks, delay_seconds=10)


ENGINE = Engine()
