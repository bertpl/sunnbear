"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``Ex. 3.10, 3.11, 3.14`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Example310(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^4 - x - 1``; the formula's interval is `[-2, 2]` (Fig. 3.11).

    Real roots 1.22074408460576 and -0.72449195900052, complex roots `-0.24812606280262 ± 1.03398206097597i`. Newton
    from `x0 = 1.25` and `x0 = -0.75`, then deflation (Ex. 3.10, Table 3.7); Durand–Kerner from complex starts (Ex.
    3.11, Table 3.8), and from the real starts 1, -1, 2, -2, where it fails (Ex. 3.14, Table 3.11).
    """

    number = (1, 4, 5, 21)
    name = "Example 3.10"
    params = ()
    location_in_publication = "Examples 3.10, 3.11, 3.14"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{4} - \tmp{u} - 1",
        interval="[-2, 2]",
        summary=(
            "A convex quartic with both of its real roots on the interval, so that the function is positive at both "
            "bounds."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**4 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.8, c=0.0, expected=0.20960000000000015),
        FormulaTestCase.value(params={}, x=-0.8, c=0.1, expected=11.297600000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 2.0)),
    )
