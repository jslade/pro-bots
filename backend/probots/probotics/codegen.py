from tatsu.model import Node
from tatsu.walkers import NodeWalker

from ..probotics.ops.all import Operation, Immediate, Primitive, PrimitiveType


class ProboticsCodeGenerator(NodeWalker):
    """Walks a parsed AST of probotics code and generates executable bits that
    can be run by the interpreter.
    """

    def __init__(self) -> None:
        self.operations: list[Operation] = []

    def walk_object(self, node: Node):
        import ipdb

        ipdb.set_trace()
        print(f"object:: {node}")

    def walk_Comment(self, node: Node):
        pass

    def walk_Expression(self, node: Node):
        self.walk(node.children())

    def walk_Term(self, node: Node):
        self.walk(node.children())

    def walk_Factor(self, node: Node):
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
        bool_val = str_val == "true"
        value = Primitive(type=PrimitiveType.BOOL, value=bool_val)
        self.operations.append(Immediate(value))

    def walk_Null(self, node: Node):
        value = Primitive(type=PrimitiveType.NULL, value=None)
        self.operations.append(Immediate(value))
