"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Moler2004Ex43(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``816*x^3 - 3835*x^2 + 6000*x - 3125``; the formula's interval is ``[1,
    2]``.

    The book calls `p(x)` a cubic with 3 closely spaced real roots. Ex. 4.3 asks for its exact roots; plots it for `1.43
    <= x <= 1.71`; runs Newton from `x0 = 1.5`, the secant method from `x0 = 1, x1 = 2`, and bisection on `[1, 2]`; and
    asks what `fzerotx(p,[1,2])` returns, and why.
    """

    number = (1, 4, 3, 14)
    name = "Ex. 4.3"
    params = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Ex. 4.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 816 * x**3 - 3835 * x**2 + 6000 * x - 3125

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-13.397999999999993),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-108.46549999999998),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
