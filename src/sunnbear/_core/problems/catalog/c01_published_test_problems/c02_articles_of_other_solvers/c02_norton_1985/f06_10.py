"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``10`` in the survey of published test problems.
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


class Norton198510(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``x^n + a*x + b``, with the parameters `a = 1, b = 10^-4`; `n = 3, 5, 9,
    19`; the formula's interval is ``[-0.7, 1]``.

    The formula's parameters ``a_`` and ``b_`` are the source's ``a`` and ``b``, renamed because ``[a, b]`` names the
    formula's interval.

    Group II.
    """

    number = (1, 2, 2, 6)
    name = "10"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("b_", latex_symbol="b"),
        FormulaParam("n", latex_symbol="n"),
    )
    source = FormulaSource(
        reference=(
            "Norton, V. (1985). Algorithm 631: Finding a bracketed zero by Larkin's method of rational "
            "interpolation. ACM Transactions on Mathematical Software 11(2), 120–134. "
            "https://doi.org/10.1145/214392.214396. The author's Fortran code is Algorithm 631 of the "
            "Collected Algorithms of the ACM (CALGO), https://www.netlib.org/toms/631."
        ),
        location="Section 4, function 10",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.7 \c"),),
        expression=r"\tmp{u}^{\param{n}} + \param{a_} \tmp{u} + \param{b_}",
        interval="[-0.7, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, b_: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.7 * c
        return x**n + a_ * x + b_

    def interval_bounds(self, a_: float, b_: float, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.7, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "b_", "n"),
                rows=((1.0, 0.0001, 3.0), (1.0, 0.0001, 5.0), (1.0, 0.0001, 9.0), (1.0, 0.0001, 19.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0001, "n": 3.0}, x=-0.19, c=0.0, expected=-0.196759),
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0001, "n": 3.0}, x=-0.19, c=0.25, expected=-0.847508375),
        FormulaTestCase.value(
            params={"a_": 1.0, "b_": 0.0001, "n": 5.0}, x=-0.19, c=0.0, expected=-0.19014760990000001
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "b_": 0.0001, "n": 9.0}, x=-0.19, c=0.0, expected=-0.18990032268769777
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "b_": 0.0001, "n": 19.0}, x=-0.19, c=0.0, expected=-0.18990000000001978
        ),
        FormulaTestCase.interval_bounds(params={"a_": 1.0, "b_": 0.0001, "n": 3.0}, expected=(-0.7, 1.0)),
    )
