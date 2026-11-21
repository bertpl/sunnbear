"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``8`` in the survey of published test problems.
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


class Norton19858(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``x^n + a*x + b``, with the parameters `a = 1, b = 0`; `n = 3, 5, 9, 19`;
    the formula's interval is ``[-0.7, 1]``.

    The formula's parameters ``a_`` and ``b_`` are the source's ``a`` and ``b``, renamed because ``[a, b]`` names the
    formula's interval.

    Group II: a simple zero, and an inflection point of order `n - 1` or `n` at or near it. The root is exactly 0; the
    article notes that Bus–Dekker's Algorithm R needs 362 evaluations for `x^3 + x` at `eps = 2^-62`, `eta = 2^-129`.
    """

    number = (1, 2, 2, 4)
    name = "8"
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
        location="Section 4, function 8",
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
                rows=((1.0, 0.0, 3.0), (1.0, 0.0, 5.0), (1.0, 0.0, 9.0), (1.0, 0.0, 19.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0, "n": 3.0}, x=-0.19, c=0.0, expected=-0.196859),
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0, "n": 3.0}, x=-0.19, c=0.25, expected=-0.847608375),
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0, "n": 5.0}, x=-0.19, c=0.0, expected=-0.1902476099),
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0, "n": 9.0}, x=-0.19, c=0.0, expected=-0.1900003226876978),
        FormulaTestCase.value(params={"a_": 1.0, "b_": 0.0, "n": 19.0}, x=-0.19, c=0.0, expected=-0.1900000000000198),
        FormulaTestCase.interval_bounds(params={"a_": 1.0, "b_": 0.0, "n": 3.0}, expected=(-0.7, 1.0)),
    )
