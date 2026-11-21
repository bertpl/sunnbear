"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Table 1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class DowellJarratt1972Table1(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``x^3 + 1``; the formula's interval is ``[-2, 0]``.

    Root `-1`. Starting values `x0 = 0`, `x1 = -2`. The formula keeps the article's form. sunnbear's
    `tests/solvers/bracketing/pegasus/test_paper.py` solves the mirrored `1 - x^3` on `[0, 2]`, because sunnbear's
    `Pegasus` takes the upper bound as its newest starting point.
    """

    number = (1, 1, 2, 1)
    name = "Table 1"
    params = ()
    source = FormulaSource(
        reference=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an '
            "equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        location="Table 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**3 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.4, c=0.0, expected=-1.7439999999999996),
        FormulaTestCase.value(params={}, x=-1.4, c=0.25, expected=-5.858999999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 0.0)),
    )
