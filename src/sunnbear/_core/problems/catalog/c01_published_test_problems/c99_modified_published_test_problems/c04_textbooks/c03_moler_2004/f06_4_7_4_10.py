"""This module holds formula f1.99.4.3.6, the modified version of the published formula f1.4.3.6.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.6 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedMoler200447410(Formula):
    """This formula is the modified version of formula f1.4.3.6, from Moler (2004).

    The survey writes the source's function as ``1/((x - 0.3)^2 + 0.01) + 1/((x - 0.9)^2 + 0.04) - 6``; the published
    interval is `[-1, 2]` (Figure 4.8).

    MATLAB's demo function `humps`, which §4.10 says illustrates graphics, quadrature and zero-finding routines; §4.7
    names the handle `@humps` as an example of syntax. The chapter uses it only for minimization: `fmintx` minimizes
    `-humps(x)` on `[-1, 2]` (§4.10, Figure 4.8; Ex. 4.17).

    The formula changes the published interval ``[-1, 2]`` to ``[-1, 1]``: its upper bound moves left of the second
    root, near 1.3, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 3, 6)
    name = "§4.7, §4.10"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§4.7, §4.10",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 1 / ((x - 0.3) ** 2 + 0.01) + 1 / ((x - 0.9) ** 2 + 0.04) - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-5.005466778805719),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
