"""This module holds formula f1.99.4.7.11, the modified version of the published formula f1.4.7.11.

A change of formula f1.4.7.11 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurdenFairesBurden2016213(Formula):
    """This formula is the modified version of formula f1.4.7.11, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 7*x^2 + 14*x - 6``; the published intervals are `[0, 1]`; `[1,
    3.2]`; `[3.2, 4]`.

    Bisection to `1E-2` on each interval (2.1-3); all zeros to `1E-5` by Newton with deflation (2.6-2).

    The formula holds only the test problem on ``[3.2, 4]``. The formula computes the published function in the
    equivalent form ``(x - 3)*((x - 2)**2 - 2)``, on that interval; ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the published interval.

    The published test problem on ``[3.2, 4]`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root ``2 + sqrt(2)``, the terms of the published form cancel, so that f is exactly 0 at many x-values
    within about 1e-14 of the root.

    In the equivalent form, ``x - 3`` and ``x - 2`` are exact on the interval, and so is the subtraction of 2 from the
    square near the root, so that near the root f is exactly 0 only where ``(x - 2)**2`` rounds to exactly 2.

    No float64 x near the root makes the square round to exactly 2, so f is exactly 0 at no x-value near the root.
    """

    number = (1, 99, 4, 7, 11)
    name = "2.1-3"
    params = ()
    location_in_publication = "Exercises 2.1-3, 2.6-2(h)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.8 \c"),),
        expression=r"\left(\tmp{u} - 3\right) \left(\left(\tmp{u} - 2\right)^{2} - 2\right)",
        interval="[3.2, 4]",
        notes=(
            (
                r"The expression equals the published function, $$\tmp{u}^{3} - 7 \tmp{u}^{2} + 14 \tmp{u} "
                "- 6,$$ without the cancellation that makes the published function exactly 0 at many "
                "x-values next to the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(y - 3)*((y - 2)**2 - 2)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.8 * c
        return (x - 3) * ((x - 2) ** 2 - 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.2, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(3.2, 4.0)),
        FormulaTestCase.value(params={}, x=3.44, c=0.25, expected=-0.11097600000000003),
    )
