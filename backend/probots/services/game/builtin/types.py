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
            return Primitive.of(Primitive.output(frame.args["value"].value))

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
        inst = cls(engine, player)

        builtins["list"] = Primitive.block(
            operations=[Native(inst.new_list)], name="list", arg_names=[]
        )

    def new_list(self, frame: StackFrame) -> Primitive:
        new_list = [arg for arg in frame.args.values()]
        return Primitive.of(new_list)


class NewObject(Builtin):
    """create a new object"""

    @classmethod
    def add(cls, player: Player, engine: "Engine", builtins: ScopeVars) -> None:
        inst = cls(engine, player)

        builtins["object"] = Primitive.block(
            operations=[Native(inst.new_object)], name="object", arg_names=[]
        )

    def new_object(self, frame: StackFrame) -> Primitive:
        new_object = {k: v for k, v in frame.args.items()}
        return Primitive.of(new_object)
