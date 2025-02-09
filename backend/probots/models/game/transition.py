from pydantic import Field

from typing import Any, Callable, Optional, TypeAlias
from ..mixins.pydantic_base import BaseSchema


TransitionCallback: TypeAlias = Callable[["Transition"], None]


class Transition(BaseSchema):
    """Represents a multistep process of going from one state to another"""

    name: str
    initial: Any
    final: Any
    current: Optional[Any]

    # Progress is measured as an integer value.
    progress: int
    remaining_steps: int

    # Non-serializing values used for processing the transition on the python side only
    on_start: Optional[TransitionCallback] = Field(None, exclude=True)
    on_update: Optional[TransitionCallback] = Field(None, exclude=True)
    on_complete: Optional[TransitionCallback] = Field(None, exclude=True)
