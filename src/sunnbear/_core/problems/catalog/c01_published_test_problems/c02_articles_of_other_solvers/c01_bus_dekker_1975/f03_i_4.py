"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``I.4`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BusDekker1975I4(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``x^2 - (1 - x)^n``, with the parameters ``n = 1, 5, 10``; the formula's
    interval is ``[0, 1]``.

    The article: 1 inflection point in `[0, 1]`.
    """

    number = (1, 2, 1, 3)
    name = "I.4"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence "
            "for finding a zero of a function. ACM Transactions on Mathematical Software 1(4), 330–345."
            " https://doi.org/10.1145/355656.355659."
        ),
        location="I.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - (1 - x) ** n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((1.0,), (5.0,), (10.0,))),)

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.61),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.9475),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.07807000000000001),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=0.06175247509999999),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
