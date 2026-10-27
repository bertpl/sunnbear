"""This module holds formula f1.99.4.3.1, the modified version of the published formula f1.4.3.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.1 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedMoler200411(Formula):
    """This formula is the modified version of formula f1.4.3.1, from Moler (2004).

    The survey writes the source's function as ``1/x - (x - 1)``; the published interval is `[0, 4]` (Figure 1.2).

    The aspect ratio equation `1/x = x - 1` of the golden rectangle, whose positive root is the golden ratio `(1 +
    sqrt(5))/2`. Besides the quadratic formula, §1.1 solves it 3 ways in MATLAB: as the polynomial `x^2 - x - 1` with
    `roots`; symbolically with `solve(1/x == x-1)`; and as `f = @(x) 1./x-(x-1)` with `fzero(f,1)`, from the starting
    point `x = 1`. `ezplot(f,0,4)` plots `f` on `[0, 4]` (Figure 1.2), where it becomes infinite as `x` tends to 0.

    The formula's interval starts at ``0.04``, right of 0 by 1% of the published interval's width, rounded half up to 1
    significant digit; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` divides by 0
    in ``1/x``.
    """

    number = (1, 99, 4, 3, 1)
    name = "§1.1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§1.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.96 * c
        return 1 / x - (x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.04, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.228, c=0.25, expected=4.963680672268908),
        FormulaTestCase.interval_bounds(params={}, expected=(0.04, 4.0)),
    )
