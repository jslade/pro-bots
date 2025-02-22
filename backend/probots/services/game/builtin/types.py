from typing import TYPE_CHECKING

import structlog

from ....models.game.player import Player
from ....probotics.ops.all import Native, Primitive, ScopeVars, StackFrame
from .base import Builtin

if TYPE_CHECKING:
    from ..engine import Engine

LOGGER = structlog.get_logger(__name__)


class ToStr(Builtin):
    """call str() on the argument"""

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_str(frame: StackFrame) -> Primitive:
            return Primitive.of(str(frame.args["value"].value))

        builtins["str"] = Primitive.block(
            operations=[Native(do_str)], name="str", arg_names=["value"]
        )


class ToInt(Builtin):
    """call int() on the argument"""

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_int(frame: StackFrame) -> Primitive:
            return Primitive.of(int(frame.args["value"].value))

        builtins["int"] = Primitive.block(
            operations=[Native(do_int)], name="int", arg_names=["value"]
        )


class NewList(Builtin):
    """create a new list"""

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_new_list(frame: StackFrame) -> Primitive:
            return Primitive.of([])

        builtins["list"] = Primitive.block(
            operations=[Native(do_new_list)], name="list", arg_names=[]
        )


class NewObject(Builtin):
    """create a new object"""

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        def do_new_object(frame: StackFrame) -> Primitive:
            return Primitive.of({})

        builtins["object"] = Primitive.block(
            operations=[Native(do_new_object)], name="object", arg_names=[]
        )
