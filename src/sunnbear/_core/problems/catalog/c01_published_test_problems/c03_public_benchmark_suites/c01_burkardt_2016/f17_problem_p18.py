"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p18`` in the survey of published test problems.
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


class Burkardt2016ProblemP18(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``10.0^14*(1.0*x^7 - 7.0*x^6 + 21.0*x^5 - 35.0*x^4 + 35.0*x^3 - 21.0*x^2
    + 7.0*x - 1.0)``; the formula's intervals are `[0.988, 1.012]` (rang); `[0.990, 1.013]` (starts 1 and 2).

    The source's starting points, in order, are `0.990` and `1.013`. The code also holds the Horner form of the
    polynomial, switched off by `horners = False`.
    """

    number = (1, 3, 1, 17)
    name = "Problem p18"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p18"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"{10.0}^{14} \left(1.0 \tmp{u}^{7} - 7.0 \tmp{u}^{6} + 21.0 \tmp{u}^{5} - 35.0 \tmp{u}^{4} "
            r"+ 35.0 \tmp{u}^{3} - 21.0 \tmp{u}^{2} + 7.0 \tmp{u} - 1.0\right)"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"$(\x - 1)^7$ written out as a polynomial and scaled by $10^{14}$, whose rounding errors decide its sign "
            r"over about 90% of the interval."
        ),
        notes=(
            (
                "The source takes this polynomial from Cleve B. Moler, Numerical Computing with MATLAB, SIAM (2004), "
                "ISBN 978-0-898716-60-3."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 10.0**14 * (
            1.0 * x**7 - 7.0 * x**6 + 21.0 * x**5 - 35.0 * x**4 + 35.0 * x**3 - 21.0 * x**2 + 7.0 * x - 1.0
        )

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.988, 1.012, 0.024), (0.99, 1.013, 0.023)),
                summary="The published intervals.",
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024},
            x=0.9952,
            c=0.0,
            expected=-0.005870683422720227,
            atol=40.0,
        ),
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024}, x=0.9952, c=0.25, expected=-1.7138242687795553, atol=40.0
        ),
        FormulaTestCase.value(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023},
            x=0.9969,
            c=0.0,
            expected=-0.00027512614110999483,
            atol=40.0,
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.988, "b": 1.012, "c_scale": 0.024}, expected=(0.988, 1.012)),
        FormulaTestCase.interval_bounds(params={"a": 0.99, "b": 1.013, "c_scale": 0.023}, expected=(0.99, 1.013)),
    )
