import random
import queue
import threading
from typing import Callable, Optional, TypeAlias

import structlog

from ...models.all import BaseSchema, Message
from ...models.game.all import Grid, Player, Probot, ProbotState, ProbotOrientation
from ..dispatcher import DISPATCHER
from ..session_service import SESSIONS
from .map_maker import MapMaker
from .processor import Processor, Work, WorkFunc

LOGGER = structlog.get_logger(__name__)


PlayerWorkFunc: TypeAlias = Callable[[Player], None]
ProbotWorkFunc: TypeAlias = Callable[[Probot], None]


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
        self.processor: Processor
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

        while not self.stopped:
            self.setup_processor()
            self.setup_game()
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

    def setup_game(self) -> None:
        LOGGER.info("Setting up fresh game state")

        mm = MapMaker()
        self.grid = mm.generate(10, 10)

        game = GameResetData(
            current=GameCurrentStateData(
                grid=self.grid,
                players=[p for p in self.players],
                probots=[p for p in self.probots],
            )
        )

        # reset players
        for player in self.players:
            self.reset_player(player)

        # reset probots:
        for probot in self.probots:
            self.reset_probot(probot)

        # Tell everyone about the new game state
        message = Message(
            type="game",
            event="reset",
            session_id="",
            data=game.model_dump(),
        )
        self.outgoing.put(message)

        # Just now for testing purposes:
        if not self.players:
            self.processor.add_work(self.spawn_test_player)

    def reset_player(self, player: Player) -> None:
        LOGGER.info("Resetting player", player=player.name)
        player.score = 0

    def reset_probot(self, probot: Probot) -> None:
        LOGGER.info("Resetting probot", probot=probot.name)

        # The old one goes away:
        # self.remove_probot(probot)

        # Create a new one from the old:
        # self.add_probot(self.duplicate_probot(probot))

    def setup_processor(self) -> None:
        LOGGER.info("Setting up processor")
        self.processor = Processor()
        self.incoming = self.processor.incoming

        # Some standard tasks
        # self.processor.add_work(self.report_ticks)
        self.processor.add_work(self.report_game_state)

    def report_ticks(self) -> None:
        # TODO: Move to a separate service
        LOGGER.info("ticks", ticks=self.processor.ticks)

        self.processor.add_work(self.report_ticks, delay_seconds=30)

    def report_game_state(self) -> None:
        # TODO: Move to a separate service
        LOGGER.info(
            "players",
            players=[
                (p.name, p.score)
                for p in sorted(self.players, key=lambda p: p.score, reverse=True)
            ],
        )
        LOGGER.info(
            "probots",
            probots=[p for p in self.probots],
        )
        LOGGER.info("\n" + self.grid.to_str())

        self.processor.add_work(self.report_game_state, delay_seconds=5)

    def add_player(self, player: Player) -> None:
        if player in self.players:
            return

        self.players.append(player)

        # Schedule work to make it run...

        LOGGER.info("Added player", player=player.name)

    def remove_player(self, player: Player) -> None:
        if player not in self.players:
            return

        self.players.remove(player)

        self.processor.cancel_work_where(
            lambda item: isinstance(item, GameWork) and item.player == player
        )

    def add_probot(self, probot: Probot) -> None:
        if probot in self.probots:
            return

        self.probots.append(probot)

        # Schedule work to make it run...
        self.add_probot_work(
            probot,
            func=self.collect_energy,
            every=10,
        )

        LOGGER.info(
            "Added probot",
            probot=probot.name,
            player=probot.player.name,
            id=probot.id,
            at=(probot.x, probot.y),
        )

    def remove_probot(self, probot: Probot) -> None:
        if probot not in self.probots:
            return

        self.probots.remove(probot)

        self.processor.cancel_work_where(
            lambda item: isinstance(item, GameWork) and item.probot == probot
        )

    def spawn_test_player(self) -> None:
        """Create a new player just for testing purposes"""
        player = Player(
            name="TEST",
            score=0,
        )
        self.add_player(player)

        probot = self.spawn_probot(player)
        self.add_probot(probot)

    def spawn_probot(self, player: Player) -> None:
        """Create a new probot controlled by the given player.
        Spawn location is random"""

        x, y = self.random_spawn_location()

        orientation = ProbotOrientation.W
        if x < self.grid.width / 2:
            if y < self.grid.height / 2:
                orientation = ProbotOrientation.E
            else:
                orientation = ProbotOrientation.S
        else:
            if y < self.grid.height / 2:
                orientation = ProbotOrientation.N

        probot = Probot(
            player=player,
            id=len(self.probots),
            name=player.name,
            x=x,
            y=y,
            orientation=orientation,
            state=ProbotState.idle,
            energy=Probot.MAX_ENERGY / 2,
            crystals=0,
        )
        self.add_probot(probot)

        return probot

    def random_spawn_location(self) -> tuple[int, int]:
        while True:
            x = random.randint(1, self.grid.width - 1)
            y = random.randint(1, self.grid.height - 1)

            if self.is_empty_cell(x, y):
                return (x, y)

    def is_empty_cell(self, x: int, y: int) -> bool:
        cell = self.grid.get(x, y)
        if cell.crystals != 0:
            return False

        for probot in self.probots:
            if probot.x == x and probot.y == y:
                return False

        return True

    def add_probot_work(
        self,
        probot: Probot,
        func: ProbotWorkFunc,
        delay: int = 0,
        every: Optional[int] = None,
        critical: bool = False,
    ) -> "GameWork":
        def once():
            func(probot)

        def repeating():
            once()

            item = self.processor.add_work(
                repeating, every, critical=critical, work_type=GameWork
            )
            item.probot = probot
            item.player = probot.player

        item = self.processor.add_work(
            repeating if every else once, delay, critical=critical, work_type=GameWork
        )
        item.probot = probot
        item.player = probot.player

        return item

    def collect_energy(self, probot: Probot) -> None:
        """Probots increase energy automatically, faster when idle"""
        # TODO: Move to a separate service of some sort
        if probot.energy >= Probot.MAX_ENERGY:
            return

        rate = 50.0

        match probot.state:
            case ProbotState.idle:
                rate *= 3.0
            case ProbotState.moving:
                rate *= 0.2
            case ProbotState.turning:
                rate *= 0.5
            case ProbotState.jumping:
                rate = 0.0

        if probot.crystals:
            rate *= 3.0

        pct = 1.0 * (probot.energy / Probot.MAX_ENERGY)
        delta_raw = rate * (1.0 - pct)
        if delta_raw <= 0:
            return

        delta = int(delta_raw) or 1
        probot.energy += delta
        if probot.energy > Probot.MAX_ENERGY:
            probot.energy = Probot.MAX_ENERGY


class GameWork(Work):
    """Some work items need to be associated with specific game entities,
    so that they can be canceled when no longer applicable"""

    player: Optional[Player]
    probot: Optional[Probot]


ENGINE = Engine()
