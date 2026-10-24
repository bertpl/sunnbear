"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``func11`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class RootsJl2026Func11(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``exp(-x) - cos(x)``; the formula's interval is `[-2, 2]` (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-2.0` to `2.0`.

    With ``modified = 1``, the interval ``[-2, 2]`` becomes ``[-2, 1]``: its upper bound moves left of the second root,
    near 1.29, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 3, 6, 4)
    name = "func11"
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
        location="func11",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(-x) - math.cos(x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.0, 2.0, 4.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.0, 1.0, 3.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.0, expected=1.5288342191453024
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.25, expected=6.276849559106034
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, expected=(-2.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 1.0, "c_scale": 3.0, "modified": 1.0}, x=-1.1, c=0.25, expected=6.635409769426345
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 1.0, "c_scale": 3.0, "modified": 1.0}, expected=(-2.0, 1.0)
        ),
    )
