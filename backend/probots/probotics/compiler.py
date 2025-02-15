from pathlib import Path

import tatsu

from .codegen import ProboticsCodeGenerator
from .ops.all import Operation


class ProboticsCompiler:
    def __init__(self) -> None:
        self.grammar = Path(__file__).with_name("probotics-grammar.ebnf").read_text()
        self.parser = tatsu.compile(self.grammar, asmodel=True)

    def compile(self, input: str) -> list[Operation]:
        model = self.parse(input)
        operations = self.codegen(model)
        return operations

    def parse(self, input: str):
        """Parse an input string into a tatsu model -- which is essentially a list of
        instances of objects. Each object is going to be something in the tatsu.synth
        module, which are a bunch of dynamically-defined dataclasses.

        The model classes are named according to the annotated types in the grammar.
        For example:
           expression::Expression = ....
        will result in an model class Expression being defined, and instances of the
        Expression class will be used to represent the parsed items.

        This object model is intended to be used by codegen()
        """
        model = self.parser.parse(input)
        return model

    def codegen(self, model) -> list[Operation]:
        """Takes an object model returned by parse() and turns it into executable
        operations. The ProboticsCodeGenerator will walk the parse tree and generate
        corresponding operations, which are the final instructions that can be
        evaluated by the interpreter"""
        codegen = ProboticsCodeGenerator()
        codegen.walk(model)
        return codegen.operations
