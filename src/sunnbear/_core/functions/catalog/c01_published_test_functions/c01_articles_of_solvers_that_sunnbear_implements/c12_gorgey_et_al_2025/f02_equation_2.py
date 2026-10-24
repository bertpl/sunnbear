"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 2`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GorgeyEtAl2025Equation2(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``log(x)``; the formula's interval is ``[0, 2]``.

    Root `1`. The text below Table 3 gives the interval `[2, 3.5]`, which holds no root of `log(x)`: the article repeats
    the interval of Equation 1 there, so the row's `interval` leaves `[2, 3.5]` out.

    With ``modified = 1``, the interval starts at ``0.02``, right of 0 by 1% of the published interval's width, rounded
    half up to 1 significant digit; ``c`` shifts x as category 1 states, with the ``c_scale`` of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because ``f(a) = log(0)`` is not
    finite.
    """

    number = (1, 1, 12, 2)
    name = "Equation 2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.log(x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 2.0, 2.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.02, 2.0, 1.98, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, x=0.6, c=0.0, expected=-0.5108256237659907
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, x=0.6, c=0.25, expected=-2.302585092994046
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, expected=(0.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.02, "b": 2.0, "c_scale": 1.98, "modified": 1.0},
            x=0.614,
            c=0.25,
            expected=-2.1286317858706076,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.02, "b": 2.0, "c_scale": 1.98, "modified": 1.0}, expected=(0.02, 2.0)
        ),
    )
