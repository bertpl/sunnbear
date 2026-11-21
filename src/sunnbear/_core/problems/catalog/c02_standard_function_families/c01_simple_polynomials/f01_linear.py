"""This formula is the line ``x + c``."""

from sunnbear._core.problems.core import EffectOfC, Formula, FormulaPresentation, FormulaTestCase, ParamRecipe


class Linear(Formula):
    """`Linear` is the line ``x + c``, whose root is at ``-c``."""

    number = (2, 1, 1)
    name = "Linear"
    presentation = FormulaPresentation(
        expression=r"\x + \c",
        interval="[-1, 1]",
        summary="A line, the simplest function with 1 root.",
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate ``x + c``."""
        return x + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipes: the formula has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.3),
        FormulaTestCase.value(params={}, x=0.3, c=-0.5, expected=-0.2),  # c shifts the value
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
