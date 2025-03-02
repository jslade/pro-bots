from contextlib import contextmanager

import structlog
from tatsu.model import Node
from tatsu.walkers import NodeWalker

from .ops.all import (
    Addition,
    Assignment,
    Break,
    Call,
    Catch,
    CompareEqual,
    CompareGreaterThan,
    CompareGreaterThanOrEqual,
    CompareLessThan,
    CompareLessThanOrEqual,
    CompareNotEqual,
    Division,
    GetIndex,
    GetProperty,
    GetValue,
    Immediate,
    Index,
    Jump,
    JumpIf,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
    MaybeCall,
    Multiplication,
    Operation,
    Primitive,
    PrimitiveType,
    Property,
    Return,
    Subtraction,
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
        # Symbol can be simple like x, or a property like x.y
        if type(node.ast) is tuple:
            self.walk_Property(node.ast)
            if not (self.is_in_context("Assignable") and not self.is_in_context("Index")):
                # If it's not on the LHS of an assignment, get the value
                # but if it is on the LHS of an assignment, and it's part of an Index,
                # then we do want to get the value...
                self.operations.append(GetProperty())
            return

        # For the case of a simple symbol:
        symbol_name = node.ast.name
        if self.is_in_context("Assignable") and not self.is_in_context("Index"):
            # When a bare symbol is on the target side of an assignment,
            # the result should be the symbol itself
            self.operations.append(Immediate(Primitive.symbol(symbol_name)))
        else:
            # Otherwise, we want the value of the symbol in the current scope
            self.operations.append(GetValue(symbol_name))

    def walk_Property(self, properties: tuple[str, ...]):
        # This will be a left-associative list of properties, object properties.
        # So for example x.y.z, we will result in ('.', ('.', 'x', 'y'), 'z')
        dot, left, right = properties
        if type(left) is tuple:
            self.walk_Property(left)
            self.operations.append(GetProperty())
        else:
            symbol_name = left.name
            self.operations.append(GetValue(symbol_name))

        symbol_name = right.name
        self.operations.append(Property(symbol_name))

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
        "=": CompareEqual,
        "==": CompareEqual,
        "===": CompareEqual,
        "!=": CompareNotEqual,
        "!==": CompareNotEqual,
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
    # Logical
    #

    MAP_LOGICAL = {
        "and": LogicalAnd,
        "or": LogicalOr,
    }

    def walk_Logical(self, node: Node):
        with self.in_context("Logical"):
            self.walk(node.left)
            self.walk(node.right)
            self.operations.append(self.MAP_LOGICAL[node.op]())

    def walk_LogicalNot(self, node: Node):
        with self.in_context("Negative"):
            self.walk(node.right)
            self.operations.append(LogicalNot())

    #
    # Assignment
    #

    def walk_Assignment(self, node: Node):
        with self.in_context("Assignment"):
            self.walk(node.target)
            self.walk(node.value)
        self.operations.append(Assignment())

        # special case of assignment of a block to a symbol:
        # the block gets the symbol's name
        if isinstance(self.operations[-2], Immediate):
            immediate = self.operations[-2]
            if immediate.value.is_block:
                block_prim = immediate.value
                name_op = self.operations[-3]
                if isinstance(name_op, Immediate):
                    name = name_op.value.value
                    block_prim.value.name = name
                elif isinstance(name_op, Property):
                    name = name_op.name
                    block_prim.value.name = name

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

        block = Primitive.block(operations, name=self.context[-1])
        self.operations.append(Immediate(block))

    def walk_BlockWithArgs(self, node: Node):
        before = self.mark()
        with self.in_context("Block"):
            self.walk(node.statements)

        arg_names = [name.name for name in node.arg_names]
        operations = self.operations[before:]
        self.operations[before:] = []

        block = Primitive.block(operations, name=self.context[-1], arg_names=arg_names)
        self.operations.append(Immediate(block))

    def walk_IfStatement(self, node: Node):
        # This JumpIf is used to skip to the else block, if the condition is false.
        jump_to_else = JumpIf(jump=0, sense=False)

        # This jump is used to skip the else block, if the if condition is true
        jump_past_else = Jump(jump=0)

        with self.in_context("IfStatement"):
            self.walk(node.condition)
            self.operations.append(jump_to_else)
            after_if = self.mark()

            self.walk(node.block)
            self.operations.append(
                Call(0, local=True)
            )  # TODO: maybe inline block instead of call
            self.operations.append(jump_past_else)
            after_block = self.mark()

            with self.in_context("ElseStatement"):
                self.walk(node.else_chain)
                if node.else_block is not None:
                    self.operations.append(Call(0, local=True))
                after_else = self.mark()

        # Set the jump targets for the if statement
        jump_to_else.jump = after_block - after_if

        jump_past_else.jump = after_else - after_block
        if jump_past_else.jump == 0:
            # If there is no else block, skip the jump
            self.operations.pop()
            jump_to_else.jump -= 1

    def walk_WhileLoop(self, node: Node):
        # This Jump is used to jump back to the top of the loop
        jump_to_top = Jump(jump=0)

        # This JumpIf is used to skip the loop if the condition is false
        jump_past_loop = JumpIf(jump=0, sense=False)

        with self.in_context("WhileLoop"):
            before_cond = self.mark()
            self.walk(node.condition)
            self.operations.append(jump_past_loop)
            after_cond = self.mark()

            self.walk(node.block)
            self.operations.append(
                Call(0, local=True)
            )  # TODO: maybe inline block instead of call
            self.operations.append(Catch({"break": 2, "next": 1}))
            self.operations.append(jump_to_top)
            after_block = self.mark()

        # Set the jump targets
        jump_to_top.jump = before_cond - after_block  # This will be negative
        jump_past_loop.jump = after_block - after_cond

    def walk_Return(self, node: Node):
        before = self.mark()
        with self.in_context("Return"):
            self.walk(node.value)
            after = self.mark()
        self.operations.append(Return(with_value=after > before))

    def walk_Break(self, node: Node):
        self.operations.append(Break())

    def walk_Next(self, node: Node):
        self.operations.append(())

    #
    # Function calls
    #

    def walk_Call(self, node: Node):
        with self.in_context("Call"):
            self.walk(node.command)
            self.walk(node.args)

        num_args = len(node.args)

        self.operations.append(Call(num_args, local=False))
        self.operations.append(Catch({"return": 1}))

    def walk_BareCommand(self, node: Node):  # NOT IMPLEMENTED
        len_before = len(self.operations)

        with self.in_context("BareCommand"):
            self.walk(node.command)
            self.walk(node.args)

        len_after = len(self.operations)
        num_args = len(node.args)

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
        if isinstance(first, GetValue):
            if num_args > 0:
                # If there are arguments, definitely treat as a function call
                self.operations.append(Call(num_args, local=False))
            else:
                self.operations.append(MaybeCall())

    #
    # Objects and lists
    #

    def walk_Index(self, node: Node):
        with self.in_context("Index"):
            self.walk(node.target)
            self.walk(node.index)

        self.operations.append(Index())

        if not self.is_in_context("Assignable"):
            self.operations.append(GetIndex())
