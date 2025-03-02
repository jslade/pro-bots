import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.ops.all import (
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
    Property,
    Return,
    Subtraction,
    GetValue,
)


class TestCompilerPrimitives:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize("input", ["", " ", "\n"])
    def test_empty(self, compiler: ProboticsCompiler, input: str):
        ops = compiler.compile(input)
        assert len(ops) == 0

    @pytest.mark.parametrize(
        "input,expected",
        [("1", 1), ("1.2", 1.2), ("0", 0), ("0.1234", 0.1234), ("123.456", 123.456)],
    )
    def test_number_is_immediate(
        self, compiler: ProboticsCompiler, input: str, expected: int | float
    ):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value == expected

    @pytest.mark.parametrize(
        "input,expected",
        [("''", ""), ("'abc'", "abc"), ('""', ""), ('"abc"', "abc")],
    )
    def test_string_is_immediate(
        self, compiler: ProboticsCompiler, input: str, expected: str
    ):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value == expected

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("abc", "abc"),
            ("ABC", "ABC"),
            ("aBc", "aBc"),
            ("aBc123", "aBc123"),
            ("_abc", "_abc"),
            ("A_B_C", "A_B_C"),
            ("B1_", "B1_"),
        ],
    )
    def test_symbol(self, compiler: ProboticsCompiler, input: str, expected: bool):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is GetValue

    @pytest.mark.parametrize(
        "input,expected",
        [("true", True), ("false", False)],
    )
    def test_bool(self, compiler: ProboticsCompiler, input: str, expected: bool):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value == expected

    @pytest.mark.parametrize(
        "input",
        ["null", "none"],
    )
    def test_null(self, compiler: ProboticsCompiler, input: str):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value is None

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("1 # whatever", 1),
            ("2 //huh?", 2),
            ("# Ignore this line\ntrue", True),
            ("// Ignore this line\nfalse", False),
            ("null\n# skipped", None),
            ("null\n// skipped", None),
            (
                "# A comment before\n"
                "'Hi' # EOL comment\n"
                "// followed by another comment\n"
                "\n"
                "# And another",
                "Hi",
            ),
        ],
    )
    def test_eol_comments(
        self, compiler: ProboticsCompiler, input: str, expected: int | float
    ):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value == expected

    # @pytest.mark.skip("Block comments are not working yet")
    @pytest.mark.parametrize(
        "input,expected",
        [
            ("1 /* whatever */", 1),
            ("/* multi-line\n" " continued */ true", True),
        ],
    )
    def test_block_comments(
        self, compiler: ProboticsCompiler, input: str, expected: int | float
    ):
        ops = compiler.compile(input)
        assert len(ops) == 1
        assert type(ops[0]) is Immediate
        assert ops[0].value.value == expected


class TestCompilerArithmetic:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "1 + 2",
                [Immediate(Primitive.of(1)), Immediate(Primitive.of(2)), Addition()],
            ),
            (
                "1 - 2",
                [Immediate(Primitive.of(1)), Immediate(Primitive.of(2)), Subtraction()],
            ),
            (
                "a * b",
                [
                    GetValue("a"),
                    GetValue("b"),
                    Multiplication(),
                ],
            ),
            (
                "b / c",
                [
                    GetValue("b"),
                    GetValue("c"),
                    Division(),
                ],
            ),
            (
                "c + 3",
                [
                    GetValue("c"),
                    Immediate(Primitive.of(3)),
                    Addition(),
                ],
            ),
            (
                "d - 4",
                [
                    GetValue("d"),
                    Immediate(Primitive.of(4)),
                    Subtraction(),
                ],
            ),
            (
                "true / false",
                [
                    Immediate(Primitive.of(True)),
                    Immediate(Primitive.of(False)),
                    Division(),
                ],
            ),
            (
                "1 + (2 - 3) / 4 * 5",
                [
                    Immediate(Primitive.of(1)),
                    Immediate(Primitive.of(2)),
                    Immediate(Primitive.of(3)),
                    Subtraction(),
                    Immediate(Primitive.of(4)),
                    Division(),
                    Immediate(Primitive.of(5)),
                    Multiplication(),
                    Addition(),
                ],
            ),
        ],
    )
    def test_arithmetic(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops

    def test_assignment(self, compiler: ProboticsCompiler):
        ops = compiler.compile("a := 1 + 2")
        assert ops == [
            Immediate(Primitive.symbol("a")),
            Immediate(Primitive.of(1)),
            Immediate(Primitive.of(2)),
            Addition(),
            Assignment(),
        ]


class TestConditionals:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("a == b", [GetValue("a"), GetValue("b"), CompareEqual()]),
            ("a != b", [GetValue("a"), GetValue("b"), CompareNotEqual()]),
            ("a < b", [GetValue("a"), GetValue("b"), CompareLessThan()]),
            ("a <= b", [GetValue("a"), GetValue("b"), CompareLessThanOrEqual()]),
            ("a > b", [GetValue("a"), GetValue("b"), CompareGreaterThan()]),
            ("a >= b", [GetValue("a"), GetValue("b"), CompareGreaterThanOrEqual()]),
        ],
    )
    def test_comparison(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops


class TestLogicals:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("a and b", [GetValue("a"), GetValue("b"), LogicalAnd()]),
            ("a or b", [GetValue("a"), GetValue("b"), LogicalOr()]),
            ("not a ", [GetValue("a"), LogicalNot()]),
            ("a and not b", [GetValue("a"), GetValue("b"), LogicalNot(), LogicalAnd()]),
            (
                "(a or b) and not (c or d)",
                [
                    GetValue("a"),
                    GetValue("b"),
                    LogicalOr(),
                    GetValue("c"),
                    GetValue("d"),
                    LogicalOr(),
                    LogicalNot(),
                    LogicalAnd(),
                ],
            ),
        ],
    )
    def test_comparison(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops


class TestBlocks:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "a := { 1 + 2 }",
                [
                    Immediate(Primitive.symbol("a")),
                    Immediate(
                        Primitive.block(
                            [
                                Immediate(Primitive.of(1)),
                                Immediate(Primitive.of(2)),
                                Addition(),
                            ],
                            name="a",
                        )
                    ),
                    Assignment(),
                ],
            ),
            (
                "a := { (b, c)\n" "    b + c\n" "}",
                [
                    Immediate(Primitive.symbol("a")),
                    Immediate(
                        Primitive.block(
                            [
                                GetValue("b"),
                                GetValue("c"),
                                Addition(),
                            ],
                            name="a",
                            arg_names=["b", "c"],
                        )
                    ),
                    Assignment(),
                ],
            ),
            (
                "a.b := { (c)   # test \n" "    true\n" "}",
                [
                    GetValue("a"),
                    Property("b"),
                    Immediate(
                        Primitive.block(
                            [
                                Immediate(Primitive.of(True)),
                            ],
                            name="b",
                            arg_names=["c"],
                        )
                    ),
                    Assignment(),
                ],
            ),
        ],
    )
    def test_block(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "if a { b }",
                [
                    GetValue("a"),
                    JumpIf(jump=2, sense=False),
                    Immediate(Primitive.block([GetValue("b")], name="IfStatement")),
                    Call(0, local=True),
                ],
            ),
            (
                "if a { b } else { c }",
                [
                    GetValue("a"),
                    JumpIf(jump=3, sense=False),
                    Immediate(Primitive.block([GetValue("b")], name="IfStatement")),
                    Call(0, local=True),
                    Jump(jump=2),
                    Immediate(Primitive.block([GetValue("c")], name="ElseStatement")),
                    Call(0, local=True),
                ],
            ),
            (
                "if a { b } else if (c) { d } else { e }",
                [
                    GetValue("a"),
                    JumpIf(jump=3, sense=False),
                    Immediate(Primitive.block([GetValue("b")], name="IfStatement")),
                    Call(0, local=True),
                    Jump(jump=7),
                    GetValue("c"),
                    JumpIf(jump=3, sense=False),
                    Immediate(Primitive.block([GetValue("d")], name="IfStatement")),
                    Call(0, local=True),
                    Jump(jump=2),
                    Immediate(Primitive.block([GetValue("e")], name="ElseStatement")),
                    Call(0, local=True),
                ],
            ),
            (
                "if a { return }",
                [
                    GetValue("a"),
                    JumpIf(jump=2, sense=False),
                    Immediate(
                        Primitive.block([Return(with_value=False)], name="IfStatement")
                    ),
                    Call(0, local=True),
                ],
            ),
        ],
    )
    def test_if(self, compiler: ProboticsCompiler, input: str, expected: list[Operation]):
        ops = compiler.compile(input)
        assert expected == ops

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "while true { false }",
                [
                    Immediate(Primitive.of(True)),
                    JumpIf(jump=4, sense=False),
                    Immediate(
                        Primitive.block(
                            [Immediate(Primitive.of(False))], name="WhileLoop"
                        )
                    ),
                    Call(0, local=True),
                    Catch({"break": 2, "next": 1}),
                    Jump(jump=-6),
                ],
            ),
            (
                "while a { if b { break } }",
                [
                    GetValue("a"),
                    JumpIf(jump=4, sense=False),
                    Immediate(
                        Primitive.block(
                            [
                                GetValue("b"),
                                JumpIf(jump=2, sense=False),
                                Immediate(Primitive.block([Break()], name="IfStatement")),
                                Call(0, local=True),
                            ],
                            name="WhileLoop",
                        )
                    ),
                    Call(0, local=True),
                    Catch({"break": 2, "next": 1}),
                    Jump(jump=-6),
                ],
            ),
            (
                """
                i := 0
                while True {
                    i := i + 1
                    if i == 5 {
                        break
                    }
                }                   
                """,
                [
                    Immediate(Primitive.symbol("i")),
                    Immediate(Primitive.of(0)),
                    Assignment(),
                    Immediate(Primitive.of(True)),
                    JumpIf(jump=4, sense=False),
                    Immediate(
                        Primitive.block(
                            [
                                Immediate(Primitive.symbol("i")),
                                GetValue("i"),
                                Immediate(Primitive.of(1)),
                                Addition(),
                                Assignment(),
                                GetValue("i"),
                                Immediate(Primitive.of(5)),
                                CompareEqual(),
                                JumpIf(jump=2, sense=False),
                                Immediate(Primitive.block([Break()], name="IfStatement")),
                                Call(0, local=True),
                            ],
                            name="WhileLoop",
                        )
                    ),
                    Call(0, local=True),
                    Catch({"break": 2, "next": 1}),
                    Jump(jump=-6),
                ],
            ),
            (
                "while true { return 5 }",
                [
                    Immediate(Primitive.of(True)),
                    JumpIf(jump=4, sense=False),
                    Immediate(
                        Primitive.block(
                            [Immediate(Primitive.of(5)), Return(with_value=True)],
                            name="WhileLoop",
                        )
                    ),
                    Call(0, local=True),
                    Catch({"break": 2, "next": 1}),
                    Jump(jump=-6),
                ],
            ),
        ],
    )
    def test_while(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops


class TestCompilerCalls:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "blah()",
                [
                    GetValue("blah"),
                    Call(0, local=False),
                    Catch({"return": 1}),
                ],
            ),
            (
                "a := b()",
                [
                    Immediate(Primitive.symbol("a")),
                    GetValue("b"),
                    Call(0, local=False),
                    Catch({"return": 1}),
                    Assignment(),
                ],
            ),
            (
                "move(1, 2) == true",
                [
                    GetValue("move"),
                    Immediate(Primitive.of(1)),
                    Immediate(Primitive.of(2)),
                    Call(2, local=False),
                    Catch({"return": 1}),
                    Immediate(Primitive.of(True)),
                    CompareEqual(),
                ],
            ),
        ],
    )
    def test_calls_with_parens(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ) -> None:
        ops = compiler.compile(input)
        assert expected == ops

    @pytest.mark.skip("Not implemented yet")
    def test_bare_command_1(self, compiler: ProboticsCompiler):
        ops = compiler.compile("move")
        assert ops == [
            GetValue("move"),
            MaybeCall(),
        ]

    @pytest.mark.skip("Not implemented yet")
    def test_bare_command_2(self, compiler: ProboticsCompiler):
        ops = compiler.compile("turn left")
        assert ops == [
            GetValue("turn"),
            GetValue("left"),
            Call(1, local=False),
        ]


class TestCompilerObjects:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "a.b",
                [GetValue("a"), Property("b"), GetProperty()],
            ),
            (
                "a.b.c",
                [
                    GetValue("a"),
                    Property("b"),
                    GetProperty(),
                    Property("c"),
                    GetProperty(),
                ],
            ),
            ("a[b]", [GetValue("a"), GetValue("b"), Index(), GetIndex()]),
            (
                'a["b"]',
                [GetValue("a"), Immediate(Primitive.of("b")), Index(), GetIndex()],
            ),
        ],
    )
    def test_get_property(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops

    @pytest.mark.parametrize(
        "input,expected",
        [
            (
                "a.b := c.d",
                [
                    GetValue("a"),
                    Property("b"),
                    GetValue("c"),
                    Property("d"),
                    GetProperty(),
                    Assignment(),
                ],
            ),
            (
                "a[b] := c",
                [
                    GetValue("a"),
                    GetValue("b"),
                    Index(),
                    GetValue("c"),
                    Assignment(),
                ],
            ),
            (
                'a.b["c"] := d',
                [
                    GetValue("a"),
                    Property("b"),
                    GetProperty(),
                    Immediate(Primitive.of("c")),
                    Index(),
                    GetValue("d"),
                    Assignment(),
                ],
            ),
            (
                "a.b[0] := c",
                [
                    GetValue("a"),
                    Property("b"),
                    GetProperty(),
                    Immediate(Primitive.of(0)),
                    Index(),
                    GetValue("c"),
                    Assignment(),
                ],
            ),
        ],
    )
    def test_set_property(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert expected == ops
