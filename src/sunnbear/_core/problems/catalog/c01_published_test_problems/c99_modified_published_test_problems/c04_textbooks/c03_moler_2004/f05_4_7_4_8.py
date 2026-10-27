"""This module holds formula f1.99.4.3.5, the modified version of the published formula f1.4.3.5.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.5 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import bessel_j0


class ModifiedMoler20044748(Formula):
    """This formula is the modified version of formula f1.4.3.5, from Moler (2004).

    The survey writes the source's function as ``J0(x)``; the published intervals are `[(n - 1)*pi, n*pi]`, `n = 1, ...,
    10` (§4.7); `[0, pi]` (§4.7, Ex. 4.7); `[0, 3.83]` (§4.8); `[0, 10*pi]` (Figure 4.2).

    §4.7 finds its first 10 zeros with `fzerotx`, 1 per interval, and plots it on `[0, 10*pi]` (Figure 4.2); it also
    calls `fzerotx(@bessj0,[0,pi])`. §4.8 steps `fzerogui` toward its first zero on `[0, 3.83]`, 3.83 being near its
    first local minimum (Figures 4.3–4.6). Ex. 4.7 calls `fzerotx(@besselj,[0 pi],0)`, which by `fzerotx`'s rule for
    extra arguments evaluates `besselj(x, 0)`, the Bessel function of order `x` at 0, and returns 3.1416; the exercise
    asks why. Ex. 4.10(a) asks for its first 10 zeros.

    The formula holds only the test problem on ``[0, 10*pi]``. It changes that interval to ``[0, 30]``: its upper bound
    moves between the last 2 roots, so that the interval holds 9 of the 10 roots.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[0, 10*pi]`` does not satisfy the benchmark suite inclusion conditions, because the
    published interval holds 10 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 3, 5)
    name = "§4.7, §4.8"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§4.7, §4.8; Ex. 4.7, 4.10(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 30.0 * c
        return bessel_j0(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 30.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=9.0, c=0.25, expected=0.5118276717359181),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 30.0)),
    )
