from dataclasses import dataclass

from .base import Operation
from .primitive import Primitive
from .stack_frame import EnterScope, ScopeVars, StackFrame


@dataclass
class Callable(Primitive):
    name: str
    arg_names: list[str]
    operations: list[Operation]


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

    def __init__(self, num_args: int):
        super().__init__()
        self.num_args = num_args

    def execute(self, frame: StackFrame) -> None:
        # First pop the actual call arguments from the stack
        call_args = [frame.pop() for _ in range(self.num_args)].reverse()

        # Then pop the callable from the stack
        func = frame.pop()
        if not isinstance(func, Callable):
            raise ValueError(f"Value is not callable: {func.value} ({func.type.value})")

        # Compare call arguments with the expected arguments
        # the function is defined to take in
        args = self.validate_args(call_args, func, frame)

        # Looks like we have a valid function call, so we can create a new frame
        new_frame = self.create_frame(func.name, args, frame)
        raise EnterScope(new_frame)

    def validate_args(
        self, args: list[Primitive], func: Callable, frame: StackFrame
    ) -> ScopeVars:
        """Validate the arguments passed to the function and create a new scope."""
        if len(func.arg_names) > 0 and len(args) < len(func.arg_names):
            raise ValueError(
                f"Function {func.name} expected {len(func.arg_names)} arguments, "
                f"but got {len(args)}"
            )

        # Any arguments that are not named will be given a default name: arg1, arg2, etc.
        arg_names = [n for n in func.arg_names]
        while len(arg_names) < len(args):
            arg_n = len(arg_names) - len(func.arg_names)
            arg_names.append(f"arg{arg_n}")

        # Create a new scope with the arguments
        scope_vars = ScopeVars()
        for name, value in zip(arg_names, args, strict=True):
            scope_vars.set(name, value)

        return scope_vars

    def create_frame(
        self, name: str, args: ScopeVars, func: Primitive, parent_frame: StackFrame
    ) -> StackFrame:
        """Create a new stack frame for the function call."""
        frame = StackFrame(
            name=f"{parent_frame.name}.{name}",
            builtins=parent_frame.builtins,
            operations=func.block,
            scope_vars=ScopeVars(),
            args=args,
            parent=parent_frame,
        )

        return frame

    def __repr__(self) -> str:
        return f"Call({self.num_args})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Call):
            return False
        return self.num_args == other.num_args


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
