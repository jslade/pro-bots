from typing import Any, Callable, Optional, TypeAlias

from pydantic import Field

from ..mixins.pydantic_base import BaseSchema

TransitionCallback: TypeAlias = Callable[["Transition"], None]


class Transition(BaseSchema):
    """Represents a multistep process of going from one state to another"""

    name: str

    # Progress is measured as an integer value, which should correspond to the
    # number of ticks needed to complete the transition
    total_steps: int
    progress: int = 0

    initial: Optional[Any] = None
    final: Optional[Any] = None
    current: Optional[Any] = None

    # Non-serializing values used for processing the transition on the python side only
    on_start: Optional[TransitionCallback] = Field(None, exclude=True)
    on_update: Optional[TransitionCallback] = Field(None, exclude=True)
    on_complete: Optional[TransitionCallback] = Field(None, exclude=True)
