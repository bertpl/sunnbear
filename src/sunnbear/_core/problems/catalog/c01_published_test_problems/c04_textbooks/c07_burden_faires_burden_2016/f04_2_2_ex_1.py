"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.2 Ex. 1; Fig. 2.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden201622Ex1(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = x^2 - 2``; the formula's interval is `[-3, 3]` (Fig. 2.2).

    Fixed points -1 and 2, from `(p + 1)*(p - 2) = 0`.
    """

    number = (1, 4, 7, 4)
    name = "§2.2 Ex. 1"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="§2.2 Example 1; Fig. 2.2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 6 \c"),),
        expression=r"\tmp{u} - \left(\tmp{u}^{2} - 2\right)",
        interval="[-3, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 6.0 * c
        return (x) - (x**2 - 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.2, c=0.0, expected=-0.6399999999999999),
        FormulaTestCase.value(params={}, x=-1.2, c=0.25, expected=-7.990000000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 3.0)),
    )
