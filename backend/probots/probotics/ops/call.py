from dataclasses import dataclass
from typing import Optional

from .base import Operation
from .primitive import Primitive
from .stack_frame import EnterScope, ScopeVars, StackFrame


@dataclass
class Block:
    operations: list[Operation]
    name: Optional[str]
    arg_names: list[str]

    def __output__(self) -> str:
        """This is what appears, for example, if the user types the name of
        a built-in function or a user-defined function in the terminal"""
        return f"Callable(name={self.name}, arg_names={self.arg_names})"


class Call(Operation):
    """Call operator for function calls.
    - First, all of the arguments (pre-evaluated) will be popped from the stack, based
      on the number of arguments the function takes.
    - Then, the callable itself will be popped.
    - After creating a new frame representing the scope of the called function,
      It will throw a EnterScope exception, which will be caught by the interpreter
      and actually enter the new scope.
    - When the new scope exits, the result will be left on the calling frame's
      result stack (by the interpreter, not handled here)
    """

    def __init__(self, num_args: int, local: bool = False):
        super().__init__()
        self.num_args = num_args
        self.local = local

    def execute(self, frame: StackFrame) -> None:
        # First pop the actual call arguments from the stack
        call_args = [frame.pop() for _ in range(self.num_args)]
        call_args.reverse()

        # Then pop the callable from the stack
        func_prim = frame.pop()
        if not func_prim.is_block:
            raise ValueError(
                f"Value is not callable: {func_prim.value} ({func_prim.type.value})"
            )
        block = func_prim.value

        # Compare call arguments with the expected arguments
        # the function is defined to take in
        args = self.validate_args(call_args, block, frame)

        # Looks like we have a valid function call, so we can create a new frame
        new_frame = self.create_frame(
            name=block.name,
            args=args,
            scope_vars=frame.scope_vars if self.local else None,
            global_vars=frame.global_vars,
            block=block,
            parent_frame=frame,
        )
        raise EnterScope(new_frame)

    def validate_args(
        self, args: list[Primitive], block: Block, frame: StackFrame
    ) -> ScopeVars:
        """Validate the arguments passed to the function and create a new scope."""
        # if len(block.arg_names) > 0 and len(args) < len(block.arg_names):
        #    raise ValueError(
        #        f"Block {block.name} expected {len(block.arg_names)} arguments, "
        #        f"but got {len(args)}"
        #    )

        # Any arguments that are not named will be given a default name: arg1, arg2, etc.
        arg_names = [n for n in block.arg_names]
        while len(arg_names) < len(args):
            arg_n = 1 + len(arg_names) - len(block.arg_names)
            arg_names.append(f"arg{arg_n}")

        # Create a new scope with the arguments
        scope_vars = ScopeVars()
        for name, value in zip(arg_names, args, strict=False):
            scope_vars[name] = value

        return scope_vars

    def create_frame(
        self,
        *,
        name: str,
        args: ScopeVars,
        scope_vars: Optional[ScopeVars],
        global_vars: ScopeVars,
        block: Block,
        parent_frame: StackFrame,
    ) -> StackFrame:
        """Create a new stack frame for the function call."""
        frame = StackFrame(
            context=parent_frame.context,
            name=f"{parent_frame.name}.{name}",
            builtins=parent_frame.builtins,
            operations=block.operations,
            global_vars=global_vars,
            scope_vars=scope_vars or ScopeVars(),
            args=args,
            parent=parent_frame,
        )

        return frame

    def __repr__(self) -> str:
        return f"Call(num_args={self.num_args}, local={self.local})"

    def __eq__(self, other: object) -> bool:
        if not super().__eq__(other):
            return False
        return self.num_args == other.num_args and self.local == other.local


class MaybeCall(Call):
    """Used in cases (bare commands) where it's not clear if the referenced symbol
    is intended to be a call or not, and it depends on the runtime result -- whether
    the symbol is callable or not.
    """

    def __init__(self) -> None:
        super().__init__(num_args=0)

    def execute(self, frame: StackFrame) -> None:
        maybe_func = frame.peek()
        if isinstance(maybe_func, Callable):
            super().execute(frame)
        else:
            # Treat it as an immediate value
            frame.push(frame.pop())
