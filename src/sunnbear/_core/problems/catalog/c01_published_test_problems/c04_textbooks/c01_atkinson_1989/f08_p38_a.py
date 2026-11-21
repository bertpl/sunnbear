"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``P38(a)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Atkinson1989P38A(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^4 - 5.7*x^3 - 0.47*x^2 + 29.865*x - 26.1602``; the formula's interval
    is ``[-3, 5]``.

    Evaluated in single and double precision, in steps of `h = 0.1`, to measure the noise; P41 finds the roots with a
    polynomial package.
    """

    number = (1, 4, 1, 8)
    name = "P38(a)"
    params = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="P38(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 8.0 * c
        return x**4 - 5.7 * x**3 - 0.47 * x**2 + 29.865 * x - 26.1602

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.6, c=0.0, expected=-42.8876),
        FormulaTestCase.value(params={}, x=-0.6, c=0.25, expected=38.89440000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 5.0)),
    )
