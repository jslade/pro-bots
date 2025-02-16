import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.interpreter import ExecutionContext, ProboticsInterpreter
from probots.probotics.ops.all import Operation, Primitive


def make_context(ops: list[Operation], results: list[Primitive]) -> ExecutionContext:
    return ExecutionContext(
        operations=ops,
        on_result=lambda result, context: results.append(result),
    )


class TestInterpreter:
    @pytest.fixture
    def compiler(self) -> ProboticsCompiler:
        return ProboticsCompiler()

    @pytest.fixture
    def interpreter(self) -> ProboticsInterpreter:
        return ProboticsInterpreter()

    def test_immediate(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile("1")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)
        interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(1)

    def test_addition(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile("1 + 2")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)
        interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(3)

    def test_arithmetic(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile("1 + (2 - 3) / 4 * 5")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)
        interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(-0.25)

    def test_assignment(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile("a := 1\n" "b := a + 2\n" "b")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)
        interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(3)
        assert context.get("a") == Primitive.of(1)
        assert context.get("b") == Primitive.of(3)
