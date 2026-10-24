"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7, §4.10`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Moler200447410(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``1/((x - 0.3)^2 + 0.01) + 1/((x - 0.9)^2 + 0.04) - 6``; the formula's
    interval is `[-1, 2]` (Figure 4.8).

    MATLAB's demo function `humps`, which §4.10 says illustrates graphics, quadrature and zero-finding routines; §4.7
    names the handle `@humps` as an example of syntax. The chapter uses it only for minimization: `fmintx` minimizes
    `-humps(x)` on `[-1, 2]` (§4.10, Figure 4.8; Ex. 4.17).

    With ``modified = 1``, the interval ``[-1, 2]`` becomes ``[-1, 1]``: its upper bound moves left of the second root,
    near 1.3, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the published interval
    holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 3, 6)
    name = "§4.7, §4.10"
    param_names = ("a", "b", "c_scale", "modified")
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
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 1 / ((x - 0.3) ** 2 + 0.01) + 1 / ((x - 0.9) ** 2 + 0.04) - 6

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.0, 2.0, 3.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.0, 1.0, 2.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 2.0, "c_scale": 3.0, "modified": 0.0}, x=-0.1, c=0.0, expected=0.843891402714932
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 2.0, "c_scale": 3.0, "modified": 0.0}, x=-0.1, c=0.25, expected=-4.92721024774247
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 2.0, "c_scale": 3.0, "modified": 0.0}, expected=(-1.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 1.0}, x=-0.4, c=0.25, expected=-5.005466778805719
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 1.0}, expected=(-1.0, 1.0)
        ),
    )
