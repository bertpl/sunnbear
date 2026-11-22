"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.1 Ex. 1, 2; Table 2.1; §2.2 Ill. (pp. 60, 62–63), Table 2.2; §2.4 Ill.
(p. 84); §2.5 Ill. (p. 89), Table 2.11`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Section21Example1(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 + 4*x^2 - 10``; the formula's interval is ``[1, 2]``.

    The chapter's running example: unique root `1.365230013` in `[1, 2]`. Bisection until the bound on the relative
    error is below `1E-4` gives `p13 = 1.365112305` (Ex. 1, Table 2.1); Theorem 2.1's bound gives 10 iterations for
    `1E-3` (Ex. 2). §2.2 rewrites it as 5 fixed-point problems, iterated from `p0 = 1.5` (Table 2.2): `g1 = x - x^3 -
    4*x^2 + 10`, which diverges; `g2 = (10/x - 4*x)^(1/2)`, which becomes undefined; `g3 = (1/2)*(10 - x^3)^(1/2)`; `g4
    = (10/(4 + x))^(1/2)`; and `g5 = x - (x^3 + 4*x^2 - 10)/(3*x^2 + 8*x)`, Newton's iteration. The second Illustration
    checks Theorem 2.4 for `g1` to `g4` on `[1, 2]`, and for `g3` on `[1, 1.5]`; it notes only that `g5` converges
    fastest. Newton and the modified Newton method (2.13) from `p0 = 1.5` (§2.4); Steffensen's method on `g4` from `p0 =
    1.5` (§2.5, Table 2.11).
    """

    number = (1, 4, 7, 3)
    name = "Section 2.1, example 1"
    params = ()
    location_in_publication = (
        "§2.1 Examples 1, 2; Table 2.1; §2.2 Ill. (pp. 60, 62–63), Table 2.2; §2.4 Ill. (p. 84); §2.5 Ill."
        " (p. 89), Table 2.11"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} + 4 \tmp{u}^{2} - 10",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + 4 * x**2 - 10

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-1.0429999999999993),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-4.4323749999999995),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
