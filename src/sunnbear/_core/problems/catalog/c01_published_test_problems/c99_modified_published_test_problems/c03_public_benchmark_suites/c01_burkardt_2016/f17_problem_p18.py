"""This module holds formula f1.99.3.1.17, the modified version of the published formula f1.3.1.17.

A change of formula f1.3.1.17 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ModifiedBurkardt2016ProblemP18(Formula):
    """This formula is the modified version of formula f1.3.1.17, from Burkardt (2016).

    The survey writes the source's function as ``10.0^14*(1.0*x^7 - 7.0*x^6 + 21.0*x^5 - 35.0*x^4 + 35.0*x^3 - 21.0*x^2
    + 7.0*x - 1.0)``; the published intervals are `[0.988, 1.012]` (rang); `[0.990, 1.013]` (starts 1 and 2).

    The source's starting points, in order, are `0.990` and `1.013`. The code also holds the Horner form of the
    polynomial, switched off by `horners = False`.

    The formula computes the published function in the equivalent form ``10.0**14*(x - 1)**7``, on the published
    intervals; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the terms of the
    published form cancel:

    - on ``[0.988, 1.012]``, f is exactly 0 at many x-values, up to about 0.01 from the root, and the conditions require
      bisection to spend a fixed number of evaluations, while bisection stops early where a midpoint lands on an exact 0
      of f;
    - on ``[0.990, 1.013]``, rounding changes f by up to about 1.5 near ``a = 0.990``, where f is about -1, so a
      shift along x by ``c_scale*c`` can change the sign of ``f(a)``, while the conditions require a range of ``c``
      of a minimum width in which ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0``.

    ``10.0**14*(x - 1)**7`` has no terms that cancel.

    The modification changes what the test problem tests, on both intervals: the source writes the polynomial term by
    term because the polynomial is difficult to evaluate accurately in that form, while ``10.0**14*(x - 1)**7`` is not
    difficult to evaluate accurately.
    """

    number = (1, 99, 3, 1, 17)
    name = "Problem p18"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p18"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"{10.0}^{14} \left(\tmp{u} - 1\right)^{7}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function so flat at its root of multiplicity 7 that the function stays below $10^{-4}$ in magnitude on "
            "more than 20% of each interval."
        ),
        notes=(
            (
                r"The expression equals the published function, $${10.0}^{14} \left(1.0 \tmp{u}^{7} - 7.0 "
                r"\tmp{u}^{6} + 21.0 \tmp{u}^{5} - 35.0 \tmp{u}^{4} + 35.0 \tmp{u}^{3} - 21.0 \tmp{u}^{2} "
                r"+ 7.0 \tmp{u} - 1.0\right),$$ without the cancellation that makes the published function "
                "exactly 0 at many x-values up to about 0.01 from the root."
            ),
            (
                "This changes what the test problem tests: the source writes the polynomial term by term "
                "to make it hard to evaluate accurately, and the expression evaluates it without that "
                "cancellation."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``10.0**14*(x - c_scale*c - 1)**7``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        return 10.0**14 * (x - 1) ** 7

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (0.988, 1.012, 0.024),
                    (0.99, 1.013, 0.023),
                ),
                summary="The published intervals.",
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.interval_bounds(params={"a": 0.988, "b": 1.012, "c_scale": 0.024}, expected=(0.988, 1.012)),
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024}, x=0.9952, c=0.25, expected=-1.7138242687795553
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.99, "b": 1.013, "c_scale": 0.023}, expected=(0.99, 1.013)),
        FormulaTestCase.value(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023}, x=0.9969, c=0.25, expected=-0.42520943728900457
        ),
    )
