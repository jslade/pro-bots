import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.ops.all import (
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
    MaybeCall,
    Multiplication,
    Operation,
    Primitive,
    Subtraction,
    ValueOf,
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
        assert type(ops[0]) is ValueOf

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
                    ValueOf("a"),
                    ValueOf("b"),
                    Multiplication(),
                ],
            ),
            (
                "b / c",
                [
                    ValueOf("b"),
                    ValueOf("c"),
                    Division(),
                ],
            ),
            (
                "c + 3",
                [
                    ValueOf("c"),
                    Immediate(Primitive.of(3)),
                    Addition(),
                ],
            ),
            (
                "d - 4",
                [
                    ValueOf("d"),
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
        ops = compiler.compile(input, trace=True)
        assert ops == expected

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
            ("a == b", [ValueOf("a"), ValueOf("b"), CompareEqual()]),
            ("a != b", [ValueOf("a"), ValueOf("b"), CompareNotEqual()]),
            ("a < b", [ValueOf("a"), ValueOf("b"), CompareLessThan()]),
            ("a <= b", [ValueOf("a"), ValueOf("b"), CompareLessThanOrEqual()]),
            ("a > b", [ValueOf("a"), ValueOf("b"), CompareGreaterThan()]),
            ("a >= b", [ValueOf("a"), ValueOf("b"), CompareGreaterThanOrEqual()]),
        ],
    )
    def test_comparison(
        self, compiler: ProboticsCompiler, input: str, expected: list[Operation]
    ):
        ops = compiler.compile(input)
        assert ops == expected


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
                            ]
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
        assert ops == expected


class TestCompilerCalls:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    def test_call_no_args(self, compiler: ProboticsCompiler):
        ops = compiler.compile("move()")
        assert ops == [
            ValueOf("move"),
            Call(0),
        ]

    @pytest.mark.skip("Not implemented yet")
    def test_bare_command_1(self, compiler: ProboticsCompiler):
        ops = compiler.compile("move")
        assert ops == [
            ValueOf("move"),
            MaybeCall(),
        ]

    @pytest.mark.skip("Not implemented yet")
    def test_bare_command_2(self, compiler: ProboticsCompiler):
        ops = compiler.compile("turn left")
        assert ops == [
            ValueOf("turn"),
            ValueOf("left"),
            Call(1),
        ]
