import queue
import random
import threading
from typing import Callable, Optional, TypeAlias

import structlog

from ...models.all import BaseSchema, Message, ProgramState, Session, User
from ...models.game.all import (
    Cell,
    Grid,
    Player,
    Probot,
    ProbotOrientation,
    ProbotState,
)
from ...probotics.ops.all import Operation
from ..dispatcher import DISPATCHER
from ..session_service import SESSIONS
from .coloring import ColoringService
from .energy import EnergyService
from .giving import GivingService
from .inspection import InspectionService
from .map_maker import MapMaker
from .movement import MovementService
from .processor import Processor, Work
from .programming import Programming
from .saying import SayingService
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
    program_state: ProgramState


class Engine:
    """The game engine runs as a separate thread(s) from the main
    application.
    """

    def __init__(self) -> None:
        # Game communication / flow
        self.ticks_per_sec = 10.0
        self.processor: Processor
        self.outgoing = queue.Queue()
        self.stopped = False
        self.paused = False

        # Game entities
        self.grid: Grid = Grid.blank(1, 1)
        self.players: list[Player] = []
        self.probots: list[Probot] = []
        self.player_startup: dict[str, list[Operation]] = {}

        # Helper services
        self.coloring = ColoringService()
        self.energy = EnergyService(self)
        self.giving = GivingService(self)
        self.inspection = InspectionService(self)
        self.mover = MovementService(self)
        self.programming = Programming(self)
        self.saying = SayingService(self)
        self.transitioner = TransitionService(self)

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
        self.grid = mm.generate(20, 15)

        game = GameResetData(current=self.construct_current_state())

        # reset players
        for player in self.players:
            self.reset_player(player)

        # reset probots:
        for probot in self.probots:
            self.reset_probot(probot)

        # Tell everyone about the new game state
        self.send_broadcast(event="reset", data=game.as_msg())

    def reset_player(self, player: Player) -> None:
        LOGGER.info("Resetting player", player=player.name)
        player.score = 0

        if player.name in self.player_startup:
            self.add_player_work(
                player,
                func=self.start_player,
                delay=10,
            )

    def reset_probot(self, probot: Probot) -> None:
        LOGGER.info("Resetting probot", probot=probot.name)
        probot.state = ProbotState.idle
        probot.energy = int(Probot.MAX_ENERGY / 2)
        probot.crystals = 0

        probot.dx = 0
        probot.dy = 0
        probot.dorient = 0

        self.add_probot_startup(probot)

    def reset_game(self, ticks_per_sec: Optional[float] = None) -> None:
        if ticks_per_sec is not None:
            self.ticks_per_sec = ticks_per_sec

        LOGGER.info("Resetting game", ticks_per_sec=self.ticks_per_sec)

        if self.processor:
            self.processor.stop()
            self.programming.reset()

    def save_user_changes(self) -> None:
        """This is a somewhat hacky way to save changes to the user object
        that are made during the game"""
        from probots.app import APP
        from probots.db import DB

        for player in self.players:
            if user := self.user_for_player(player):
                user.display_name = player.display_name
                user.color_body = player.colors.body
                user.color_head = player.colors.head
                user.color_tail = player.colors.tail

        with APP.app_context():
            DB.session.commit()

    def setup_processor(self) -> None:
        LOGGER.info("Setting up processor", ticks_per_sec=self.ticks_per_sec)
        self.processor = Processor(ticks_per_sec=self.ticks_per_sec)
        self.incoming = self.processor.incoming

        # Someefandard tasks
        self.processor.add_work(self.report_ticks)

    def construct_current_state(self) -> GameCurrentStateData:
        return GameCurrentStateData(
            grid=self.grid,
            players=[p for p in self.players],
            probots=[p for p in self.probots],
        )

    def report_ticks(self) -> None:
        # TODO: Move to a separate service
        LOGGER.info(
            "ticks",
            queue=id(self.processor),
            ticks=self.processor.ticks,
            len=len(self.processor.work_queue),
        )

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

    def add_player(
        self,
        player: Player,
        session: Optional[Session] = None,
        start_ops: Optional[list[Operation]] = None,
    ) -> None:
        if player in self.players:
            return

        self.players.append(player)
        if session:
            player.session_id = session.id

        # Schedule work to make it run...
        if start_ops:
            self.player_startup[player.name] = start_ops
            self.add_player_work(
                player,
                func=self.start_player,
                delay=10,
            )

        LOGGER.info(
            "Added player",
            player=player.name,
            name=player.display_name,
            session=session.id if session else None,
            user=session.user.name if session and session.user else None,
        )

        # Notify all sessions
        self.processor.add_work(self.broadcast_current_state, delay=10)

    def start_player(self, player: Player) -> None:
        """Run the startup ops for a player"""
        if player.name not in self.player_startup:
            return

        LOGGER.info("Running player startup", player=player.name)

        ops = self.player_startup[player.name]

        self.programming.execute(
            operations=ops,
            player=player,
            replace_program=True,
            replace_globals=True,
        )

    def get_player(self, name: str) -> Optional[Player]:
        for player in self.players:
            if player.name == name or player.display_name == name:
                return player

        return None

    def player_session(self, player: Player) -> Optional[Session]:
        return SESSIONS.get_session(player.session_id)

    def user_for_player(self, player: Player) -> Optional[User]:
        if session := self.player_session(player):
            return session.user

        return None

    def player_for_user(self, user: User) -> Optional[Player]:
        for player in self.players:
            if player.name == user.name:
                return player

    def player_for_session(self, session: Session) -> Optional[Player]:
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
        if player.score < 0:
            player.score = 0

        update = GameScoreUpdate(
            player_name=player.name,
            new_score=player.score,
            program_state=player.program_state,
        )

        self.send_broadcast("update_score", update.as_msg())

    def add_probot(self, probot: Probot) -> None:
        if probot in self.probots:
            return

        self.probots.append(probot)

        # Schedule work to make it run...
        self.add_probot_startup(probot)

        LOGGER.info(
            "Added probot",
            probot=probot.name,
            player=probot.player.name,
            id=probot.id,
            at=(probot.x, probot.y),
        )

    def add_probot_startup(self, probot: Probot) -> None:
        self.add_probot_work(
            probot,
            func=self.energy.collect_energy,
            repeat_interval=10,
        )
        self.add_probot_work(
            probot,
            func=self.ensure_not_stopped,
            repeat_interval=100,
        )
        self.add_probot_work(
            probot,
            func=self.wakeup_probot,
            repeat_interval=50,
        )

    def probot_for_session(self, session: Session) -> Optional[Probot]:
        for probot in self.probots:
            if probot.player.session_id == session.id:
                return probot

    def probot_for_player(self, player: Player) -> Optional[Probot]:
        for probot in self.probots:
            if probot.player == player:
                return probot

    def remove_probot(self, probot: Probot) -> None:
        if probot not in self.probots:
            return

        self.probots.remove(probot)

        self.processor.cancel_work_where(
            lambda item: isinstance(item, GameWork) and item.probot == probot
        )

    def spawn_probot(
        self, player: Player, pos: Optional[tuple[int, int, ProbotOrientation]] = None
    ) -> Probot:
        """Create a new probot controlled by the given player.
        Spawn location is random"""

        if pos:
            x, y, orientation = pos
            if not self.is_empty_cell(x, y):
                raise ValueError("illegal spawn location")
        else:
            x, y = self.random_spawn_location()
            orientation = random.choice(list(ProbotOrientation))

        probot = Probot(
            player=player,
            colors=player.colors,
            id=len(self.probots),
            name=player.name,
            x=x,
            y=y,
            orientation=orientation,
            state=ProbotState.idle,
            energy=int(Probot.MAX_ENERGY / 2),
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

    def get_cell(self, x: int, y: int) -> tuple[Cell, Optional[Probot]]:
        cell = self.grid.get(x, y)

        for probot in self.probots:
            if probot.x == x and probot.y == y:
                return [cell, probot]

        return [cell, None]

    def is_empty_cell(self, x: int, y: int, ignore_crystals: bool = True) -> bool:
        cell, probot = self.get_cell(x, y)
        if probot is not None:
            return False

        if cell.crystals != 0 and not ignore_crystals:
            return False

        return True

    def add_player_work(
        self,
        player: Player,
        func: PlayerWorkFunc,
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

    def ensure_not_stopped(self, probot: Probot) -> None:
        """Periodic task just to make sure a probot doesn't get stuck in a stopped state.
        This is really just a workaround for a bug somewhere else that is preventing
        the probot_idle callback from being called (and thus the resume_player()
        doesn't happen, the players context stays in a stopped state)"""
        self.programming.resume_player(probot.player)

    def probot_idle(self, probot: Probot) -> None:
        """This is called whenever a probot is done with a task and is now idle."""
        probot.state = ProbotState.idle

        self.programming.resume_player(probot.player)
        self.notify_of_probot_change(probot)

        self.programming.emit_event("idle", probot.player, {})

    def wakeup_probot(self, probot: Probot) -> None:
        """This is called periodically to wake up a probot that is idle.
        This allows for event-based behaviors that change periodically"""
        if probot.state == ProbotState.idle:
            self.programming.emit_event("on_wakeup", probot.player, {})

    def notify_of_player_change(self, player: Player) -> None:
        """ "Send a message to all sessions about the change in this player.
        Ideally would send a delta of some sort, but simple/dumb implementation
        is to just send the full player state"""
        self.send_broadcast(
            event="update_player",
            data=player.as_msg(),
        )

    def notify_of_probot_change(self, probot: Probot) -> None:
        """ "Send a message to all sessions about the change in this probot.
        Ideally would send a delta of some sort, but simple/dumb implementation
        is to just send the full probot state"""
        self.send_broadcast(
            event="update_probot",
            data=probot.as_msg(),
        )

    def notify_of_current_state(self, session: Session) -> None:
        self.send_to_session(
            session=session,
            type="game",
            event="current_state",
            data=self.construct_current_state().as_msg(),
        )

    def broadcast_current_state(self) -> None:
        self.send_broadcast(
            event="current_state",
            data=self.construct_current_state().as_msg(),
        )

    def send_to_player(
        self,
        player: Player,
        type: str,
        event: str,
        data: dict,
    ) -> None:
        session = self.player_session(player)
        if session:
            self.send_to_session(session, type, event, data)

    def send_to_session(
        self,
        session: Session,
        type: str,
        event: str,
        data: dict,
    ) -> None:
        message = Message(
            type=type,
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
