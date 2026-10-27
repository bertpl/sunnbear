"""This module holds formula f1.99.3.6.4, the modified version of the published formula f1.3.6.4.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.6.4 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedRootsJl2026Func11(Formula):
    """This formula is the modified version of formula f1.3.6.4, from Roots.jl (2026).

    The survey writes the source's function as ``exp(-x) - cos(x)``; the published interval is `[-2, 2]` (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-2.0` to `2.0`.

    The formula changes the interval ``[-2, 2]`` to ``[-2, 1]``: its upper bound moves left of the second root, near
    1.29, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with ``c_scale`` the
    rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.

    The modification changes what the test problem tests: the source gives ``[-2, 2]`` to ``find_zeros``, which finds
    every zero in an interval, and a solver on ``[-2, 1]`` finds 1 of the 2 roots in ``[-2, 2]``.
    """

    number = (1, 99, 3, 6, 4)
    name = "func11"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Roots.jl v3.0.11, the test folder https://github.com/JuliaMath/Roots.jl/tree/v3.0.11/test,"
            " MIT license. The functions of the rows are in 2 files:\n"
            "- `test/test_derivative_free.jl`, "
            "https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/test_derivative_free.jl\n"
            "- `test/runbenchmarks.jl`, "
            "https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/runbenchmarks.jl\n"
            "\n"
            "The files cite 1 source: the comment `## multiplicity: "
            "http://ir.igsnrr.ac.cn/bitstream/311030/8840/1/%E4%BE%AF%E9%BA%9F%E7%A7%91(SCI)2.pdf` "
            "stands above `func13` in `test_derivative_free.jl`. The URL gives no title; its file name "
            "decodes to `侯麟科(SCI)2.pdf`.\n"
            "\n"
            "The paper at the URL is Li et al. (2010): Li, X., Mu, C., Ma, J., Hou, L. (2011). "
            "Fifth-order iterative method for finding multiple roots of nonlinear equations. Numerical "
            "Algorithms 57(3), 389–398, published online in 2010. "
            "https://doi.org/10.1007/s11075-010-9434-5. Its rows are in `2010_li_multiple_roots`."
        ),
        location="func11",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.exp(-x) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=6.635409769426345),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
