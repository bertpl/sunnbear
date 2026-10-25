"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§1.1`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Moler200411(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``1/x - (x - 1)``; the formula's interval is `[0, 4]` (Figure 1.2).

    The aspect ratio equation `1/x = x - 1` of the golden rectangle, whose positive root is the golden ratio `(1 +
    sqrt(5))/2`. Besides the quadratic formula, §1.1 solves it 3 ways in MATLAB: as the polynomial `x^2 - x - 1` with
    `roots`; symbolically with `solve(1/x == x-1)`; and as `f = @(x) 1./x-(x-1)` with `fzero(f,1)`, from the starting
    point `x = 1`. `ezplot(f,0,4)` plots `f` on `[0, 4]` (Figure 1.2), where it becomes infinite as `x` tends to 0.

    With ``modified = 1``, the interval starts at ``0.04``, right of 0 by 1% of the published interval's width, rounded
    half up to 1 significant digit; ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new
    interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` divides by 0
    in ``1/x``.
    """

    number = (1, 4, 3, 1)
    name = "§1.1"
    param_names = ("a", "b", "c_scale", "modified")
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
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 1 / x - (x - 1)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 4.0, 4.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.04, 4.0, 3.96, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 4.0, "c_scale": 4.0, "modified": 0.0}, x=1.2, c=0.0, expected=0.6333333333333334
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 4.0, "c_scale": 4.0, "modified": 0.0}, x=1.2, c=0.25, expected=5.800000000000002
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 4.0, "c_scale": 4.0, "modified": 0.0}, expected=(0.0, 4.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.04, "b": 4.0, "c_scale": 3.96, "modified": 1.0}, x=1.228, c=0.25, expected=4.963680672268908
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.04, "b": 4.0, "c_scale": 3.96, "modified": 1.0}, expected=(0.04, 4.0)
        ),
    )
