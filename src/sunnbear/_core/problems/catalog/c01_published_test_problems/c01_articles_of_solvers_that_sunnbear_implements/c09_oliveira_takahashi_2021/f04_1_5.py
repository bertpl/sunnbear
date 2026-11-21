"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi202115(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``x + x^10 - 1``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 4)
    name = "1.5"
    params = ()
    source = FormulaSource(
        reference=(
            "Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method "
            "average performance preserving minmax optimality. ACM Transactions on Mathematical "
            "Software 47(1), Article 5. https://doi.org/10.1145/3423597. The article itself is dated "
            "December 2020."
        ),
        location="Table 1, well-behaved function 5",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u} + \tmp{u}^{10} - 1",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x + x**10 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-1.3998951424000001),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-1.5513215598999999),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
