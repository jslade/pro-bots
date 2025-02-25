from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, TypeAlias

import structlog

from .base import Operation
from .primitive import Primitive

ScopeVars: TypeAlias = dict[str, Primitive]


if TYPE_CHECKING:
    from ..interpreter import ExecutionContext

LOGGER = structlog.get_logger(__name__)


class UndefinedSymbol(Exception):
    pass


class EnterScope(Exception):
    """Exception to be raised when entering a new scope."""

    # The frame to enter
    frame: "StackFrame"

    def __init__(self, frame: "StackFrame") -> None:
        super().__init__()
        self.frame = frame


class ExitScope(Exception):
    """Exception to be raised when a scope is done and should be exited."""

    # The frame that is exiting, and it's return value
    frame: "StackFrame"
    return_value: "Primitive"

    def __init__(self, frame: "StackFrame", return_value: "Primitive") -> None:
        super().__init__()
        self.frame = frame
        self.return_value = return_value


@dataclass
class StackFrame:
    """Stack frame is the runtime context for operations to be executed.
    It has a list of instructions to run in order, and a a stack of values(results)
    that are passed as arguments to operations.
    """

    context: "ExecutionContext"

    name: str
    builtins: ScopeVars
    global_vars: ScopeVars
    scope_vars: ScopeVars
    args: ScopeVars
    parent: Optional["StackFrame"] = None

    operations: list["Operation"] = None
    op_index: int = 0
    results: list[Primitive] = None

    def next_op(self) -> Operation:
        """ "Get the next operation to execute and advance the index.
        If the end of the operations is reached, raise the ExitScope exception.
        """
        if self.operations is None or self.op_index >= len(self.operations):
            return_value = self.pop() if self.results else None
            raise ExitScope(self, return_value)

        op = self.operations[self.op_index]
        self.op_index += 1
        return op

    def peek_op(self) -> Optional[Operation]:
        """ "Get the next operation to execute but don't advance the index."""
        if self.operations is None or self.op_index >= len(self.operations):
            return None

        return self.operations[self.op_index]

    def get(self, name: str) -> Primitive:
        """Get the value of a symbol in the current scope."""
        try:
            return self.args.get(
                name,  # Get from args first
                self.scope_vars.get(
                    name,  # Get from local scope next
                    self.global_vars.get(
                        name,  # Get from the global scope next
                        self.builtins.get(
                            name  # Get from the builtins last
                        ),
                    ),
                ),
            )
        except KeyError:
            raise UndefinedSymbol(f"No value for {name}")

    def set(self, name: str, value: Primitive):
        """Set the value of a symbol in the current scope."""
        if name in self.args:
            # Arguments can be updated
            self.args[name] = value
            return

        if name in self.scope_vars:
            # Already a defined local -- update it
            self.scope_vars[name] = value
            return

        if name in self.global_vars:
            # Already a defined global -- update it
            self.global_vars[name] = value
            return

        if name in self.builtins:
            # Builtins are not updatable
            raise ValueError(f"Cannot assign to builtin: {name}")

        # Otherwise, add it to the local scope
        # This will be the same as the global vars for the outer frame
        self.scope_vars[name] = value

    def push(self, value: Primitive) -> None:
        """Add a value to the result stack"""
        if self.results is None:
            self.results = []
        self.results.append(value)

    def pop(self) -> Primitive:
        """Remove a value from the result stack and return it."""
        if self.results is None or len(self.results) == 0:
            raise ValueError("Stack is empty")
        return self.results.pop()

    def peek(self) -> Optional[Primitive]:
        """Look at the top value on the stack, if it exists, without removing it."""
        if self.results is None or len(self.results) == 0:
            return None
        return self.results[-1]

    @classmethod
    def make_outer(
        cls,
        context: "ExecutionContext",
        operations: list[Operation],
        builtins: ScopeVars,
        globals: ScopeVars,
    ) -> "StackFrame":
        """Create a stack frame for the operations. This will always be an outer
        frame with no parent, so the only scope vars are the global ones"""
        frame = StackFrame(
            context=context,
            name="<outer>",
            builtins=builtins,
            global_vars=globals,
            scope_vars=globals,
            args={},
            operations=operations,
            op_index=0,
            results=[],
        )
        return frame


class PushFrame(Operation):
    """Create a new scope -- a new frame on the frame stack.
    This creates a new stack frame with local variables and a separate
    instruction pointer."""

    def __init__(self, name: str, operations: list[Operation]) -> None:
        self.name = name
        self.operations = operations

    def execute(self, parent_frame: StackFrame) -> None:
        new_frame = StackFrame(
            name=self.name,
            builtins=parent_frame.builtins,
            scope_vars={},
            args={},
            parent=parent_frame,
            operations=self.operations,
            op_index=0,
            results=[],
        )
        raise EnterScope(new_frame)
