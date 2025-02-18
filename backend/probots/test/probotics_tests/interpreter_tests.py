from typing import Optional

import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.interpreter import ExecutionContext, ProboticsInterpreter
from probots.probotics.ops.all import Native, Operation, Primitive, ScopeVars


def make_context(
    ops: list[Operation], results: list[Primitive], builtins: Optional[ScopeVars] = None
) -> ExecutionContext:
    return ExecutionContext(
        operations=ops,
        builtins=builtins,
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

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("1 == 1", Primitive.of(True)),
            ("1 != 1", Primitive.of(False)),
            ("1 < 2", Primitive.of(True)),
            ("1 >= 2", Primitive.of(False)),
            ("1 > 2", Primitive.of(False)),
            ("1 <= 2", Primitive.of(True)),
            ("a:=3\nb:=4\na<b", Primitive.of(True)),
        ],
    )
    def test_comparison(
        self,
        compiler: ProboticsCompiler,
        interpreter: ProboticsInterpreter,
        input: str,
        expected: Primitive,
    ):
        ops = compiler.compile(input)
        results = []
        context = make_context(ops, results)
        interpreter.add(context)
        interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == expected

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

    def test_native(self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter):
        def do_native(frame) -> Primitive:
            return Primitive.of(1 + frame.get("arg1").value)

        builtins = {"native": Primitive.block([Native(do_native)], name="native_test")}

        ops = compiler.compile("native(1)")
        results = []
        context = make_context(ops, results, builtins)
        interpreter.add(context)

        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(2)
