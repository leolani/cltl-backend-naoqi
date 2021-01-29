from cltl.demo.api import ExampleComponent, ExampleOutput, ExampleInput


class DummyExampleComponent(ExampleComponent):
    def foo_bar(self, input: ExampleInput) -> ExampleOutput:
        return ExampleOutput(("foo bar",) * input.times, input.times)