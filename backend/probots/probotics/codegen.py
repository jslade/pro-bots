from contextlib import contextmanager

import structlog
from tatsu.model import Node
from tatsu.walkers import NodeWalker

from .ops.all import (
    Addition,
    Assignment,
    Call,
    CompareEqual,
    CompareGreaterThan,
    CompareGreaterThanOrEqual,
    CompareLessThan,
    CompareLessThanOrEqual,
    CompareNotEqual,
    Division,
    Immediate,
    Jump,
    JumpIf,
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

    def mark(self):
        """Mark the current position in the operations list."""
        return len(self.operations)

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
    # Conditionals
    #

    MAP_CONDITION = {
        "==": CompareEqual,
        "!=": CompareNotEqual,
        "<": CompareLessThan,
        "<=": CompareLessThanOrEqual,
        ">": CompareGreaterThan,
        ">=": CompareGreaterThanOrEqual,
    }

    def walk_Condition(self, node: Node):
        with self.in_context("Condition"):
            self.walk(node.left)
            self.walk(node.right)
            self.operations.append(self.MAP_CONDITION[node.op]())

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
    # Blocks
    #

    def walk_Block(self, node: Node):
        before = self.mark()
        with self.in_context("Block"):
            self.walk(node.statements)

        operations = self.operations[before:]
        self.operations[before:] = []

        block = Primitive.block(operations)
        self.operations.append(Immediate(block))

    def walk_IfStatement(self, node: Node):
        # This JumpIf is used to skip to the else block, if the condition is false.
        jump_if_op = JumpIf(jump=0, sense=False)

        # This jump is used to skip the else block, if the if condition is true
        jump_op = Jump(jump=0)

        with self.in_context("IfStatement"):
            self.walk(node.condition)
            self.operations.append(jump_if_op)
            after_if = self.mark()

            self.walk(node.block)
            self.operations.append(Call(0))  # TODO: maybe inline block instead of call
            self.operations.append(jump_op)
            after_block = self.mark()

            self.walk(node.else_chain)
            if node.else_block is not None:
                self.operations.append(Call(0))
            after_else = self.mark()

        # Set the jump targets for the if statement
        jump_if_op.jump = after_block - after_if

        jump_op.jump = after_else - after_block
        if jump_op.jump == 0:
            # If there is no else block, skip the jump
            self.operations.pop()

    #
    # Function calls
    #

    def walk_Call(self, node: Node):
        len_before = len(self.operations)

        with self.in_context("Call"):
            self.walk(node.command)
            self.walk(node.args)

        len_after = len(self.operations)
        num_args = len_after - len_before - 1

        self.operations.append(Call(num_args))

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
