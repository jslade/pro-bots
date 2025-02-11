import queue
import random
import threading
from typing import Callable, Optional, TypeAlias

import structlog

from ...models.all import BaseSchema, Message, Session, User
from ...models.game.all import Cell, Grid, Player, Probot, ProbotOrientation, ProbotState
from ..dispatcher import DISPATCHER
from ..session_service import SESSIONS
from .map_maker import MapMaker
from .movement import MovementService
from .processor import Processor, Work
from .transitioner import TransitionService

LOGGER = structlog.get_logger(__name__)


PlayerWorkFunc: TypeAlias = Callable[[Player], None]
ProbotWorkFunc: TypeAlias = Callable[[Probot], None]


class GameCurrentStateData(BaseSchema):
    grid: Grid
    players: list[Player]
    probots: list[Probot]


class GameResetData(BaseSchema):
    current: GameCurrentStateData


class GameScoreUpdate(BaseSchema):
    player_name: str
    new_score: int


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
        self.player_sessions: {}

        # Helper services
        self.transitioner = TransitionService(self)
        self.mover = MovementService(self)

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
        # LOGGER.info("OUTGOING", message=message)
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

        game = GameResetData(current=self.construct_current_state())

        # reset players
        for player in self.players:
            self.reset_player(player)

        # reset probots:
        for probot in self.probots:
            self.reset_probot(probot)

        # Tell everyone about the new game state
        self.send_broadcast(event="reset", data=game.model_dump(by_alias=True))

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
        self.add_game_work(
            self.report_game_state, repeat_interval_seconds=10
        )  # TODO: For testing

    def construct_current_state(self) -> GameCurrentStateData:
        return GameCurrentStateData(
            grid=self.grid,
            players=[p for p in self.players],
            probots=[p for p in self.probots],
        )

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

        def decorate_cell(cell: Cell, value: str) -> str:
            for probot in self.probots:
                if probot.x == cell.x and probot.y == cell.y:
                    value = "<{:02d}>".format(probot.id)
            return value

        LOGGER.info("\n" + self.grid.to_str(decorator=decorate_cell))

    def randomly_move(self, probot: Probot) -> None:
        # TODO: This is just for testing
        r = random.randint(0, 4)
        match r:
            case 0:
                self.mover.move(probot, backward=True)
            case 1:
                self.mover.turn(probot, "left")
            case 2:
                self.mover.turn(probot, "right")
            case _:
                self.mover.move(probot)

    def add_player(self, player: Player, session: Optional[Session] = None) -> None:
        if player in self.players:
            return

        self.players.append(player)
        if session:
            player.session_id = session.id

        # Schedule work to make it run...

        LOGGER.info(
            "Added player",
            player=player.name,
            session=session.id if session else None,
            user=session.user.name if session and session.user else None,
        )

        # Notify all sessions
        self.processor.add_work(self.broadcast_current_state, delay=10)

    def player_session(self, player: Player) -> Optional[Session]:
        return SESSIONS.get_session(player.session_id)

    def player_for_user(self, user: User) -> Optional[Session]:
        for player in self.players:
            if player.name == user.name:
                return player

    def player_for_session(self, session: Session) -> Optional[Session]:
        for player in self.players:
            if player.session_id == session.id:
                return player

    def remove_player(self, player: Player) -> None:
        if player not in self.players:
            return

        self.players.remove(player)

        self.processor.cancel_work_where(
            lambda item: isinstance(item, GameWork) and item.player == player
        )

        # Notify all sessions
        self.processor.add_work(self.broadcast_current_state, delay=10)

    def update_score(self, player: Player, delta: int) -> None:
        player.score += delta

        update = GameScoreUpdate(player_name=player.name, new_score=player.score)

        self.send_broadcast("update_score", update.model_dump(by_alias=True))

    def add_probot(self, probot: Probot) -> None:
        if probot in self.probots:
            return

        self.probots.append(probot)

        # Schedule work to make it run...
        self.add_probot_work(
            probot,
            func=self.collect_energy,
            repeat_interval=10,
        )

        LOGGER.info(
            "Added probot",
            probot=probot.name,
            player=probot.player.name,
            id=probot.id,
            at=(probot.x, probot.y),
        )

    def probot_for_session(self, session: Session) -> Optional[Probot]:
        for probot in self.probots:
            if probot.player.session_id == session.id:
                return probot

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

        # self.add_probot_work(
        #    probot, self.randomly_move, delay=10, repeat_interval_seconds=1
        # )

    def spawn_probot(self, player: Player) -> Probot:
        """Create a new probot controlled by the given player.
        Spawn location is random"""

        x, y = self.random_spawn_location()

        orientation = random.choice(list(ProbotOrientation))

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

    def is_empty_cell(self, x: int, y: int, ignore_crystals: bool = True) -> bool:
        for probot in self.probots:
            if probot.x == x and probot.y == y:
                return False

        cell = self.grid.get(x, y)
        if cell.crystals != 0 and not ignore_crystals:
            return False

        return True

    def add_player_work(
        self,
        player: Player,
        func: ProbotWorkFunc,
        delay: int = 0,
        delay_seconds: float = 0,
        repeat_interval: Optional[int] = None,
        repeat_interval_seconds: Optional[float] = None,
        critical: bool = False,
    ) -> "GameWork":
        """Add a work callback that takes a player as an argument"""

        def once():
            func(player)

        return self.add_game_work(
            func=once,
            delay=delay,
            delay_seconds=delay_seconds,
            repeat_interval=repeat_interval,
            repeat_interval_seconds=repeat_interval_seconds,
            critical=critical,
            player=player,
        )

    def add_probot_work(
        self,
        probot: Probot,
        func: ProbotWorkFunc,
        delay: int = 0,
        delay_seconds: float = 0,
        repeat_interval: Optional[int] = None,
        repeat_interval_seconds: Optional[float] = None,
        critical: bool = False,
    ) -> "GameWork":
        """Add a work callback that takes a probot as an argument"""

        def once():
            func(probot)

        return self.add_game_work(
            func=once,
            delay=delay,
            repeat_interval=repeat_interval,
            repeat_interval_seconds=repeat_interval_seconds,
            critical=critical,
            probot=probot,
            player=probot.player,
        )

    def add_game_work(
        self,
        func: ProbotWorkFunc,
        delay: int = 0,
        delay_seconds: float = 0,
        repeat_interval: Optional[int] = None,
        repeat_interval_seconds: Optional[float] = 0,
        critical: bool = False,
        probot: Optional[Probot] = None,
        player: Optional[Player] = None,
    ) -> "GameWork":
        if repeat_interval or repeat_interval_seconds:
            once = func

            def repeating():
                once()

                item = self.processor.add_work(
                    repeating,
                    delay=repeat_interval or 0,
                    delay_seconds=repeat_interval_seconds,
                    critical=critical,
                    work_type=GameWork,
                )
                item.probot = probot
                item.player = probot.player if probot else None

            func = repeating

        item = self.processor.add_work(
            func,
            delay=delay,
            delay_seconds=delay_seconds,
            critical=critical,
            work_type=GameWork,
        )
        item.probot = probot
        item.player = probot.player if probot else None

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

    def notify_of_probot_change(self, probot: Probot) -> None:
        """ "Send a message to all sessions about the change in this probot.
        Ideally would send a delta of some sort, but simple/dumb implementation
        is to just send the full probot state"""
        self.send_broadcast(
            event="probot_update",
            data=probot.model_dump(by_alias=True),
        )

    def notify_of_current_state(self, session: Session) -> None:
        self.send_to_session(
            session=session,
            event="current_state",
            data=self.construct_current_state().model_dump(by_alias=True),
        )

    def broadcast_current_state(self) -> None:
        self.send_broadcast(
            event="current_state",
            data=self.construct_current_state().model_dump(by_alias=True),
        )

    def send_to_player(self, player: Player, event: str, data: dict) -> None:
        session = self.player_session(player)
        if session:
            self.send_to_session(session, event, data)

    def send_to_session(self, session: Session, event: str, data: dict) -> None:
        message = Message(
            type="game",
            event=event,
            session_id=session.id,
            data=data,
        )
        self.outgoing.put(message)

    def send_broadcast(self, event: str, data: dict) -> None:
        message = Message(
            type="game",
            event=event,
            session_id="",  # empty string means broadcast to the dispatcher
            data=data,
        )
        self.outgoing.put(message)


class GameWork(Work):
    """Some work items need to be associated with specific game entities,
    so that they can be canceled when no longer applicable"""

    player: Optional[Player]
    probot: Optional[Probot]


ENGINE = Engine()
