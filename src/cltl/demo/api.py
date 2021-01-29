from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass
class ExampleInput:
    """Domain object for the input.
    """
    value: str
    times: int

@dataclass
class ExampleOutput:
    """Domain object for the input.
    """
    value: Tuple[str]
    length: int


class ExampleComponent:
    """
    Abstract class defining the interface of the component.

    This is not mandatory, but makes it easier to get an idea of what
    the module does and is a good place to put documentation.
    """

    def foo_bar(self, input: ExampleInput) -> ExampleOutput:
        """
        Foo bar, multiple times.

        Parameters
        ----------
        input : ExampleInput
            Input of the component.

        Returns
        -------
        ExampleOutput
            The result of foo bar.
        """
        raise NotImplementedError("")
