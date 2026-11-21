"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``(1.2)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class SuliMayers200312(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``1/2 - 1/(1 + M*abs(x - 1.05))``, with the parameters given per
    interval, on `[0.8, 1.8]`: `M = 200` (Fig. 1.1), `M = 2000, 20000, 200000, 2000000, 20000000` (Remark 1.1); on
    `[1.04999, 1.05001]`: `M = 2000000, 20000000` (Remark 1.1); the formula's intervals are `[0.8, 1.8]`; `[1.04999,
    1.05001]`.

    2 roots, `1.05 - 1/M` and `1.05 + 1/M`, only `2/M` apart. Remark 1.1 asks the reader to plot it in Maple for each
    `M`, and to replot it on the smaller interval for the 2 largest `M`. A footnote in Section 1.6 (p. 28) notes that
    bisection applies although `f` is not differentiable at 1.05.
    """

    number = (1, 4, 2, 1)
    name = "(1.2)"
    params = (
        FormulaParam("M", latex_symbol="M"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge "
            "University Press, Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        location="Eq. (1.2)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{1}{2} - \frac{1}{1 + \param{M} \left|{\tmp{u} - 1.05}\right|}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, M: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 1 / 2 - 1 / (1 + M * abs(x - 1.05))

    def interval_bounds(self, M: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("M", "a", "b", "c_scale"),
                rows=(
                    (200.0, 0.8, 1.8, 1.0),
                    (2000.0, 0.8, 1.8, 1.0),
                    (20000.0, 0.8, 1.8, 1.0),
                    (200000.0, 0.8, 1.8, 1.0),
                    (2000000.0, 0.8, 1.8, 1.0),
                    (20000000.0, 0.8, 1.8, 1.0),
                    (2000000.0, 1.04999, 1.05001, 2e-05),
                    (20000000.0, 1.04999, 1.05001, 2e-05),
                ),
                summary="The published parameter values and intervals.",
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(
            params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.4090909090909092
        ),
        FormulaTestCase.value(
            params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.25, expected=0.47560975609756095
        ),
        FormulaTestCase.value(
            params={"M": 2000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.4900990099009901
        ),
        FormulaTestCase.value(
            params={"M": 20000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.499000999000999
        ),
        FormulaTestCase.value(
            params={"M": 200000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.4999000099990001
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.499990000099999
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, x=1.1, c=0.0, expected=0.499999000001
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05},
            x=1.05,
            c=0.0,
            expected=-0.49999999991118216,
            atol=2e-08,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05},
            x=1.05,
            c=0.0,
            expected=-0.4999999991118216,
            atol=2e-07,
        ),
        FormulaTestCase.interval_bounds(params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0}, expected=(0.8, 1.8)),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05}, expected=(1.04999, 1.05001)
        ),
    )
