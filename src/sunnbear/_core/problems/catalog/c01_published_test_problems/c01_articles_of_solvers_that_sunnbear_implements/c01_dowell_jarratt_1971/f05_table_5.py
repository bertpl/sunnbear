"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class DowellJarratt1971Table5(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``(1 + (1 - n)^4)*x - (1 - n*x)^4``, with the parameters ``n = 2, 5, 15,
    20``; the formula's interval is ``[0, 1]``.

    The caption says the function has 1 turning point and 1 inflection point on `[0, 1]`.
    """

    number = (1, 1, 1, 5)
    name = "Table 5"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (1 + (1 - n) ** 4) * x - (1 - n * x) ** 4

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,))),)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=0.5744),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.25, expected=-0.5561),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=77.0375),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=11375.0375),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=38471.6),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
