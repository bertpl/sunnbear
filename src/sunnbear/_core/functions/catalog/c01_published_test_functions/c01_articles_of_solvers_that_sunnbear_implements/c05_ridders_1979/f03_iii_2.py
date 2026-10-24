"""This module holds a formula of Ridders (1979).

The formula comes from the row with the key ``III.2`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Ridders1979Iii2(Formula):
    """This formula comes from Ridders (1979).

    The survey writes the source's function as ``tan(x)^tan(x) - 10^3``; the formula's intervals are `[1.3, 1.4]`; `[0,
    1.5]`.

    Last printed iterate: `1.354710442`.

    With ``modified = 1``, the interval ``[0, 1.5]`` becomes ``[0.02, 1.5]``: its lower bound moves right of 0 by 1% of
    the published interval's width, rounded half up to 1 significant digit; ``c`` shifts x as category 1 states, with
    ``c_scale`` the rounded width of the new interval.

    The published test function on ``[0, 1.5]`` fails a benchmark suite's checks of its test functions, because a shift
    along x by any ``c > 0`` evaluates ``tan(x)^tan(x)`` left of ``a = 0``, where the base ``tan(x)`` is negative.
    """

    number = (1, 1, 5, 3)
    name = "III.2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous"
            " function. IEEE Transactions on Circuits and Systems 26(11), 979–980. "
            "https://doi.org/10.1109/TCS.1979.1084580."
        ),
        location="III.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.tan(x) ** math.tan(x) - 10**3

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (1.3, 1.4, 0.1, 0.0),
                    (0.0, 1.5, 1.5, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.02, 1.5, 1.48, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.3, "b": 1.4, "c_scale": 0.1, "modified": 0.0}, x=1.33, c=0.0, expected=-695.5887196520625
        ),
        FormulaTestCase.value(
            params={"a": 1.3, "b": 1.4, "c_scale": 0.1, "modified": 0.0}, x=1.33, c=0.25, expected=-880.9903886606878
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.5, "c_scale": 1.5, "modified": 0.0}, x=0.45, c=0.0, expected=-999.2963560197811
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.3, "b": 1.4, "c_scale": 0.1, "modified": 0.0}, expected=(1.3, 1.4)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 1.5, "c_scale": 1.5, "modified": 0.0}, expected=(0.0, 1.5)
        ),
        FormulaTestCase.value(
            params={"a": 0.02, "b": 1.5, "c_scale": 1.48, "modified": 1.0}, x=0.464, c=0.25, expected=-999.1995954429276
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.02, "b": 1.5, "c_scale": 1.48, "modified": 1.0}, expected=(0.02, 1.5)
        ),
    )
