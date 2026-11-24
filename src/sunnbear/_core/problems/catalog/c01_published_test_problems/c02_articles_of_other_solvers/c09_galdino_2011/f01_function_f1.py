"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011FunctionF1(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's interval is ``[2.5, 3.5]``.

    The appendix states a zero of multiplicity 3 at `x = 3`. The Scilab script of Section IV solves it on `[2.5, 3.5]`.
    """

    number = (1, 2, 9, 1)
    name = "Function f1"
    params = ()
    location_in_publication = "Table IV, f1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u} + 2\right) \left(\tmp{u} + 1\right) \left(\tmp{u} - 3\right)^{3}",
        interval="[2.5, 3.5]",
        summary=(
            "A quintic whose 1 root on the interval is triple, with values below 0.021 in magnitude within 0.1 of that "
            "root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.8, c=0.0, expected=-0.14592000000000038),
        FormulaTestCase.value(params={}, x=2.8, c=0.25, expected=-1.4718965625000016),
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.5)),
    )
