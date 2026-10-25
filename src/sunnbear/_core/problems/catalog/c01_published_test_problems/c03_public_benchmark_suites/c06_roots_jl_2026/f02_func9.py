"""This module holds a formula of Roots.jl (2026).

The formula comes from the rows with the keys ``func9`` and ``f7`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's rows in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class RootsJl2026Func9(Formula):
    """This formula comes from Roots.jl (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - func9: ``tanh(x) - tan(x)``; the formula's interval is `[5, 12]` (`find_zeros`)
    - f7: ``tanh(x) - tan(x)``; the formula's interval is ``[4.0, 8.0]``

    func9: The source's 8 starting points are evenly spaced from `5.0` to `10.0`.

    f7: The source's starting point is `x0 = 7.6`.

    With ``modified = 1``, the interval ``[5, 12]`` becomes ``[5, 7.7]``: its upper bound moves left of the pole of
    ``tan(x)`` at ``5*pi/2``, near 7.85, so that the interval holds 1 root and no pole.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[5, 12]`` does not satisfy the benchmark suite inclusion conditions, because the
    function's 2 roots and the 2 poles of ``tan(x)`` give 4 sign changes in the published interval, so that ``f(a)`` and
    ``f(b)`` have the same sign.

    With ``modified = 1``, the modification changes what the test problem tests: the source gives ``[5, 12]`` to
    ``find_zeros``, which finds every zero in an interval, and ``[5, 7.7]`` holds 1 root and no pole.
    """

    number = (1, 3, 6, 2)
    name = "func9"
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
        location="func9, f7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.tanh(x) - math.tan(x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (5.0, 12.0, 7.0, 0.0),
                    (4.0, 8.0, 4.0, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((5.0, 7.7, 2.7, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 5.0, "b": 12.0, "c_scale": 7.0, "modified": 0.0}, x=7.1, c=0.0, expected=-0.06489448847872395
        ),
        FormulaTestCase.value(
            params={"a": 5.0, "b": 12.0, "c_scale": 7.0, "modified": 0.0}, x=7.1, c=0.25, expected=2.349779305773395
        ),
        FormulaTestCase.value(
            params={"a": 4.0, "b": 8.0, "c_scale": 4.0, "modified": 0.0}, x=5.2, c=0.0, expected=2.885581014405963
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 5.0, "b": 12.0, "c_scale": 7.0, "modified": 0.0}, expected=(5.0, 12.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.0, "b": 8.0, "c_scale": 4.0, "modified": 0.0}, expected=(4.0, 8.0)
        ),
        FormulaTestCase.value(
            params={"a": 5.0, "b": 7.7, "c_scale": 2.7, "modified": 1.0}, x=5.81, c=0.25, expected=3.22359613381936
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 5.0, "b": 7.7, "c_scale": 2.7, "modified": 1.0}, expected=(5.0, 7.7)
        ),
    )
