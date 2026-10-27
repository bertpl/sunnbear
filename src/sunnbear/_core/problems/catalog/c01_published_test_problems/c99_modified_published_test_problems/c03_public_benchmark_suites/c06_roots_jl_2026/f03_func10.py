"""This module holds formula f1.99.3.6.3, the modified version of the published formula f1.3.6.3.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.6.3 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedRootsJl2026Func10(Formula):
    """This formula is the modified version of formula f1.3.6.3, from Roots.jl (2026).

    The survey writes the source's function as ``asin(x^2 - 1) - x/2 + 1``; the published interval is `[-0.5, 1.0]`
    (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-0.5` to `0.9`.

    The formula changes the interval ``[-0.5, 1]`` to ``[-0.2, 1]``: its lower bound moves right of the first root,
    near -0.30, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.

    The modification changes what the test problem tests: the source gives ``[-0.5, 1]`` to ``find_zeros``, which finds
    every zero in an interval, and a solver on ``[-0.2, 1]`` finds 1 of the 2 roots in ``[-0.5, 1]``.
    """

    number = (1, 99, 3, 6, 3)
    name = "func10"
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
        location="func10",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return math.asin(x**2 - 1) - x / 2 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.2, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.16, c=0.25, expected=-0.3024816100652327),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.2, 1.0)),
    )
