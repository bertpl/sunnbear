"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``func10`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class RootsJl2026Func10(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``asin(x^2 - 1) - x/2 + 1``; the formula's interval is `[-0.5, 1.0]`
    (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-0.5` to `0.9`.

    With ``modified = 1``, the interval ``[-0.5, 1]`` becomes ``[-0.2, 1]``: its lower bound moves right of the first
    root, near -0.30, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale``
    the rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the published interval
    holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 3, 6, 3)
    name = "func10"
    param_names = ("a", "b", "c_scale", "modified")
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
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.asin(x**2 - 1) - x / 2 + 1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-0.5, 1.0, 1.5, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-0.2, 1.0, 1.2, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -0.5, "b": 1.0, "c_scale": 1.5, "modified": 0.0}, x=-0.05, c=0.0, expected=-0.4750709089923888
        ),
        FormulaTestCase.value(
            params={"a": -0.5, "b": 1.0, "c_scale": 1.5, "modified": 0.0}, x=-0.05, c=0.25, expected=0.2521800920193261
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.5, "b": 1.0, "c_scale": 1.5, "modified": 0.0}, expected=(-0.5, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -0.2, "b": 1.0, "c_scale": 1.2, "modified": 1.0}, x=0.16, c=0.25, expected=-0.3024816100652327
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.2, "b": 1.0, "c_scale": 1.2, "modified": 1.0}, expected=(-0.2, 1.0)
        ),
    )
