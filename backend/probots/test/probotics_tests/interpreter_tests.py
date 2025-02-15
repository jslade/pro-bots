import pytest

from probots.probotics.interpreter import ExecutionContext, ProboticsInterpreter
from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.ops.base import Immediate, Operation, Primitive


def make_context(ops: list[Operation], results: list[Primitive]) -> ExecutionContext:
    return ExecutionContext(
        operations=ops,
        on_result=lambda result: results.append(result),
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
