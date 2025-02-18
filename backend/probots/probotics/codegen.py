from contextlib import contextmanager

import structlog
from tatsu.model import Node
from tatsu.walkers import NodeWalker

from .ops.all import (
    Addition,
    Assignment,
    Call,
    Division,
    Immediate,
    MaybeCall,
    Multiplication,
    Operation,
    Primitive,
    PrimitiveType,
    Subtraction,
    ValueOf,
)

LOGGER = structlog.get_logger(__name__)


class ProboticsCodeGenerator(NodeWalker):
    """Walks a parsed AST of probotics code and generates executable bits that
    can be run by the interpreter.
    """

    def __init__(self) -> None:
        self.operations: list[Operation] = []
        self.context = []

    @contextmanager
    def in_context(self, name: str):
        self.context.append(name)
        # LOGGER.debug("entering context", name=".".join(self.context))
        yield
        self.context.pop()

    def is_in_context(self, name: str) -> bool:
        return name in self.context

    #
    # Catch-all
    #
    def walk_object(self, node: Node):
        # import ipdb

        # ipdb.set_trace()
        LOGGER.warning("walker not defined", node=node.__repr__())

    #
    # High-level constructs
    #

    def walk_Comment(self, node: Node):
        pass

    def walk_Statement(self, node: Node):
        with self.in_context("Statement"):
            self.walk(node.children())

    def walk_Expression(self, node: Node):
        with self.in_context("Expression"):
            self.walk(node.children())

    def walk_Term(self, node: Node):
        with self.in_context("Term"):
            self.walk(node.children())

    def walk_Factor(self, node: Node):
        with self.in_context("Factor"):
            self.walk(node.children())

    #
    # Primitives
    #

    def walk_Atom(self, node: Node):
        with self.in_context("Atom"):
            self.walk(node.children())

    def walk_Number(self, node: Node):
        i_val, d_val = node.ast
        if d_val:
            num = float(f"{i_val}{d_val}")
            value = Primitive(type=PrimitiveType.FLOAT, value=num)
        else:
            num = int(i_val)
            value = Primitive(type=PrimitiveType.INT, value=num)
        self.operations.append(Immediate(value))

    def walk_String(self, node: Node):
        str_val = node.ast[1:-1]
        value = Primitive(type=PrimitiveType.STRING, value=str_val)
        self.operations.append(Immediate(value))

    def walk_Bool(self, node: Node):
        str_val = node.ast
        bool_val = str_val == "true" or str_val == "True"
        value = Primitive(type=PrimitiveType.BOOL, value=bool_val)
        self.operations.append(Immediate(value))

    def walk_Null(self, node: Node):
        value = Primitive(type=PrimitiveType.NULL, value=None)
        self.operations.append(Immediate(value))

    def walk_Symbol(self, node: Node):
        symbol_name = node.ast
        if self.is_in_context("Assignable"):
            # When a bare symbol is on the target side of an assignment,
            # the result should be the symbol itself
            self.operations.append(Immediate(Primitive.symbol(symbol_name)))
        else:
            # Otherwise, we want the value of the symbol in the current scope
            self.operations.append(ValueOf(symbol_name))

    #
    # Arithmetic
    #

    def walk_Addition(self, node: Node):
        self.walk(node.left)
        self.walk(node.right)
        self.operations.append(Addition())

    def walk_Subtraction(self, node: Node):
        self.walk(node.left)
        self.walk(node.right)
        self.operations.append(Subtraction())

    def walk_Multiplication(self, node: Node):
        self.walk(node.left)
        self.walk(node.right)
        self.operations.append(Multiplication())

    def walk_Division(self, node: Node):
        self.walk(node.left)
        self.walk(node.right)
        self.operations.append(Division())

    #
    # Assignment
    #

    def walk_Assignment(self, node: Node):
        with self.in_context("Assignment"):
            self.walk(node.target)
            self.walk(node.value)
        self.operations.append(Assignment())

    def walk_Assignable(self, node: Node):
        with self.in_context("Assignable"):
            self.walk(node.children())

    #
    # Function calls
    #

    def walk_BareCommand(self, node: Node):  # NOT IMPLEMENTED
        len_before = len(self.operations)

        with self.in_context("BareCommand"):
            self.walk(node.command)
            self.walk(node.args)

        len_after = len(self.operations)
        num_args = len_after - len_before - 1

        # Is the first child op added a symbol? Then it may be a symbol that
        # resolves to a function call, but can't determine until runtime.
        first = self.operations[len_before]
        LOGGER.debug(
            "bare command",
            len_before=len_before,
            len_after=len_after,
            num_args=num_args,
            first=first,
        )
        if isinstance(first, ValueOf):
            if num_args > 0:
                # If there are arguments, definitely treat as a function call
                self.operations.append(Call(num_args))
            else:
                self.operations.append(MaybeCall())
