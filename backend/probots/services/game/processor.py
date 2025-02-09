import functools
import heapq
import queue
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, ClassVar, Optional, Self, Type, TypeAlias

import structlog

from ...models.all import Message

LOGGER = structlog.get_logger(__name__)

WorkFunc: TypeAlias = Callable[[], None]


@functools.total_ordering
@dataclass
class Work:
    """Represents work that needs to be done to advance the game state.
    Any callable function can be scheduled as work to run in the queue.
    """

    func: WorkFunc
    id: int
    not_before_ticks: int
    critical: bool = False

    TOTAL_COUNT: ClassVar[int] = 0

    @classmethod
    def next_id(cls) -> int:
        i = cls.TOTAL_COUNT
        cls.TOTAL_COUNT += 1
        return i

    def __lt__(self, other: Self) -> bool:
        """Comparison is based on scheduled tick time. If they are
        scheduled for the same tick, tie-breaker based on id, assuming
        lower id means it was created first, so should run first"""
        if self.not_before_ticks < other.not_before_ticks:
            return True
        if self.not_before_ticks == other.not_before_ticks:
            return self.id < other.id
        return False

    def __eq__(self, other: Self) -> bool:
        return self.not_before_ticks == other.not_before_ticks and self.id == other.id


class WorkQueue:
    def __init__(self) -> None:
        self.heap = []
        heapq.heapify(self.heap)

    def push(self, item: Work) -> None:
        heapq.heappush(self.heap, item)

    def pop(self) -> Optional[Work]:
        if self.is_empty():
            return None
        return heapq.heappop(self.heap)

    def peek(self) -> Optional[Work]:
        if self.is_empty():
            return None
        return self.heap[0]

    def remove(self, item: Work) -> None:
        try:
            self.heap.remove(item)
            heapq.heapify(self.heap)
        except ValueError:
            pass

    def remove_where(self, predicate: Callable[[Work], bool]) -> None:
        try:
            self.heap = [i for i in self.heap if not predicate(i)]
            heapq.heapify(self.heap)
        except ValueError:
            pass

    def __len__(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        return len(self.heap) == 0


class Processor:
    """Low-level "operating system" of the game / simulation

    It manages a work queue, which are just chunks of work that needs to be
    done. It processes the items in the queue as quickly as possible, but also
    idling when possible.

    The work items each have a "not_before" attribute, which is used to order
    them in a priority queue. The "not_before" is measured in ticks. A tick is
    a (fractional) number of seconds, but the length of a tick is tunable,
    which sets the overall speed of the game

    In addition to the work queue, there is also a queue of incoming messages that
    will be processed as quickly as possible, in the order they are received.
    The work queue is not thread-safe, because it is expected that the only things
    adding to or removing from the queue will happen within the thread the
    Processor is running it. But the message queue is expected to be receiving
    items from other threads.
    """

    def __init__(self, ticks_per_sec: float = 10.0) -> None:
        # Managing game communication and flow
        self.ticks = 0
        self.ticks_per_sec = ticks_per_sec  # Game speed, not the same as frame rate

        self.tick_interval = timedelta(seconds=1.0 / self.ticks_per_sec)

        self.stopped = False
        self.paused = False

        self.work_queue = WorkQueue()

        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()

    def run(self) -> None:
        """This is the entrypoint for the processor, and it will run continuously
        until it is stopped"""
        LOGGER.info("Processor started", ticks_per_sec=self.ticks_per_sec)
        started_at = datetime.now()

        self.tick_until_stopped()

        elapsed = datetime.now() - started_at
        LOGGER.info(
            "Processor ended",
            elapsed=elapsed,
            ticks=self.ticks,
        )

    def tick_until_stopped(self) -> None:
        LOGGER.info("Running game loop", tick_interval=self.tick_interval)

        while not self.stopped:
            now = datetime.now()

            if self.paused:
                time.sleep(self.tick_interval.total_seconds())
                continue

            self.ticks += 1

            until = now + self.tick_interval

            # All enqueued messages are processed immediately
            self.process_all_incoming(until)

            # Do as much work as possible -- at least one, even if processing
            # incoming messages took all the time.
            # We still need to move things forward
            self.process_work(until)

        LOGGER.info("Game thread terminating")

    def process_all_incoming(self, until: datetime) -> None:
        while True:
            try:
                received: Message = self.incoming.get(block=False)
                self.process_incoming(received)
                self.incoming.task_done()
            except queue.Empty:
                break

            now = datetime.now()
            if now >= until:
                break

    def process_incoming(self, message: Message):
        # TODO: how does the dispatcher fit into this? Non-game messages
        # should not get into the game thread, so some level of dispatching
        # will need to happen in the main thread context.
        # Game-specific messages need to be processed in the game thread..
        # so does the dispatcher have a handler that just routes all game*
        # messages to the engine's incoming queue?
        # Or maybe / in addition there is a second dispatcher that is
        # used here, that is only dispatching to handlers within the game thread?
        pass

    def process_work(self, until: datetime) -> None:
        """Process as many items from the work queue as possible"""

        while True:
            next_work = self.work_queue.peek()
            if next_work is None or self.ticks < next_work.not_before_ticks:
                # No work available during this tick, so sleep it off
                now = datetime.now()
                if now < until:
                    sleep_duration = until - now
                    time.sleep(sleep_duration.total_seconds())
            else:
                try:
                    work = self.work_queue.pop()
                    work.func()
                except Exception as e:
                    LOGGER.exception(e)
                    if work.critical:
                        self.stop()

            now = datetime.now()
            if now >= until:
                break

    def add_work(
        self,
        func: WorkFunc,
        delay: int = 0,
        delay_seconds: float = 0,
        critical: bool = False,
        work_type: Type[Work] = Work,
    ) -> Work:
        if delay <= 0:
            if delay_seconds > 0:
                delay = int(delay_seconds / self.tick_interval.total_seconds())

        work = work_type(
            func=func,
            id=work_type.next_id(),
            not_before_ticks=self.ticks + delay,
            critical=critical,
        )
        self.work_queue.push(work)

        # LOGGER.info("pushed", work=func, id=work.id)
        return work

    def cancel_work(self, item: Work) -> None:
        self.work_queue.remove(item)

    def cancel_work_where(self, predicate: Callable[[Work], bool]) -> None:
        self.work_queue.remove_where(predicate)

    def stop(self) -> None:
        LOGGER.info("Processor stopped")
        self.stopped = True

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False
