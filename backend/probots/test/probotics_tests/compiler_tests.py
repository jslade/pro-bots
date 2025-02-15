import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.ops.base import Immediate


class TestCompiler:
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

    @pytest.mark.skip("Block comments are not working yet")
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
