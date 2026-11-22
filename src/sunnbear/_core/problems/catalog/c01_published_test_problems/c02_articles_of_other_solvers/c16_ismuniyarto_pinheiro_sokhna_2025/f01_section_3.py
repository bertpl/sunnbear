"""This module holds a formula of Ismuniyarto, Pinheiro, Sokhna (2025).

The formula comes from the row with the key ``§3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class IsmuniyartoPinheiroSokhna2025Section3(Formula):
    """This formula comes from Ismuniyarto, Pinheiro, Sokhna (2025).

    The survey writes the source's function as ``-2000*1.2^n/(1.2^n - 1) + 50*n/(1.2^n - 1) + 3750 - (-600*(1 +
    0.20)^n/(1.2^n - 1) + 200*n/(1.2^n - 1))``; the formula's interval is ``[2, 10]``.

    The variable is the year `n`. The article does not print `f(n)`; the row's `f` is the AMD equation minus the Intel
    Pentium equation. The article prints the 2 equations as `A_t = -600*(1 + 0.20)^n/(1.2)^(n - 1) + 200*n/1.2^(n - 1)`
    (Intel Pentium) and `A_t = -2000*(1..2)^n/(1.2)^(n - 1) + [50*n/(1.2)^(n - 1)] + 3750` (AMD). Each printed
    denominator, `(1.2)^(n - 1)` or `1.2^(n - 1)`, is a misprint for `1.2^n - 1`, and the printed `(1..2)` is a misprint
    for `1.2`: with both readings, the row's `f` reproduces every value of `f(n)` in Table 2 and the printed `f(a)*f(b)
    = -2711558.49`, while with the denominators as printed, the difference of the 2 equations has the same sign at 2 and
    at 10. Bisection gives the root 3.22949. The article gives no starting points for the secant method; Table 2's
    secant iterates follow from the first starting point 10 and the second starting point 2, but its first relative
    error, 0.76560, is measured from 10.
    """

    number = (1, 2, 16, 1)
    name = "Section 3"
    params = ()
    location_in_publication = "§3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{n}", r"\x - 8 \c"),),
        expression=(
            r"- \frac{2000 {1.2}^{\tmp{n}}}{{1.2}^{\tmp{n}} - 1} + \frac{50 \tmp{n}}{{1.2}^{\tmp{n}} - "
            r"1} + 3750 - \left(- \frac{600 \left(1 + 0.2\right)^{\tmp{n}}}{{1.2}^{\tmp{n}} - 1} + "
            r"\frac{200 \tmp{n}}{{1.2}^{\tmp{n}} - 1}\right)"
        ),
        interval="[2, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 8.0 * c
        return (
            -2000 * 1.2**x / (1.2**x - 1)
            + 50 * x / (1.2**x - 1)
            + 3750
            - (-600 * (1 + 0.20) ** x / (1.2**x - 1) + 200 * x / (1.2**x - 1))
        )

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.4, c=0.0, expected=675.8506311323191),
        FormulaTestCase.value(params={}, x=4.4, c=0.25, expected=-856.170946467351),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 10.0)),
    )
