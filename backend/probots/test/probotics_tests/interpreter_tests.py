from typing import Optional

import pytest

from probots.probotics.compiler import ProboticsCompiler
from probots.probotics.interpreter import ExecutionContext, ProboticsInterpreter
from probots.probotics.ops.all import Native, Operation, Primitive, ScopeVars, StackFrame


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

    def test_call(self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter):
        ops = compiler.compile("foo := { 2 * 3 }\n" "foo()")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)

        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(6)

    def test_native(self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter):
        def do_native(frame: StackFrame) -> Primitive:
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

    def test_if_else(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile("if 1 > 2 { 3 } else { 4 }")
        results = []
        context = make_context(ops, results)
        interpreter.add(context)

        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(4)

    def test_while_break(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile(
            """
            i := 0
            while True {
                i := i + 1
                if i == 5 {
                    break
                }
            }
            i
            """
        )
        results = []
        context = make_context(ops, results)
        interpreter.add(context)

        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(5)

    def test_logicals(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        ops = compiler.compile(
            """
            a := True
            b := False
            c := True
            d := False
            (a or b) and not (c or d)
            """
        )
        results = []
        context = make_context(ops, results)
        interpreter.add(context)

        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(False)

    def test_object_property(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        def new_object(frame: StackFrame) -> Primitive:
            return Primitive.of({})

        builtins = {"object": Primitive.block([Native(new_object)], name="object")}

        ops = compiler.compile(
            """
            x := object()
            x.y
            x.z := 1
            x.z
            x.q := object()
            x.q.r := x.z + 1
            x.q.r
        """
        )
        results = []

        context = make_context(ops, results, builtins)
        interpreter.add(context)
        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of(2)

    def test_object_index(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        def new_object(frame: StackFrame) -> Primitive:
            return Primitive.of({})

        def new_list(frame: StackFrame) -> Primitive:
            return Primitive.of([])

        builtins = {
            "object": Primitive.block([Native(new_object)], name="object"),
            "list": Primitive.block([Native(new_list)], name="list"),
        }

        ops = compiler.compile(
            """
            x := object()
            x.y := list()
            x.y[0] := 1
            x["z"] := x["y"]
            x.z
        """
        )
        results = []

        context = make_context(ops, results, builtins)
        interpreter.add(context)
        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of([Primitive.of(1)])

    def test_str_concat(
        self, compiler: ProboticsCompiler, interpreter: ProboticsInterpreter
    ):
        def to_str(frame: StackFrame) -> Primitive:
            return Primitive.of(str(frame.get("value").value))

        builtins = {
            "str": Primitive.block([Native(to_str)], name="str", arg_names=["value"])
        }

        ops = compiler.compile(
            """
            name := "joe"
            score := 10
            x := str("hi " + name + " your score is " + str(score))
            """
        )
        results = []

        context = make_context(ops, results, builtins)
        interpreter.add(context)
        while not interpreter.is_finished:
            interpreter.execute_next()

        assert len(results) == 1
        assert results[0] == Primitive.of("hi joe your score is 10")
