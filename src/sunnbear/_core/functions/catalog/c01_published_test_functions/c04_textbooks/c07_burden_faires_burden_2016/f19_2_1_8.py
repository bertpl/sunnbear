"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-8; 2.2-16`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016218(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = tan(x)``; the formula's interval is `[4, 5]` (2.2-16).

    The first positive solution by bisection to `1E-5` (2.1-8); the solution in `[4, 5]` by fixed-point iteration to
    `1E-4` (2.2-16).

    With ``modified = 1``, the interval ``[4, 5]`` becomes ``[4, 4.6]``: its upper bound moves left of the pole of
    ``tan(x)`` at ``3*pi/2``, near 4.71, so that the interval holds its root and no pole.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the pole inside the
    interval is a second sign change, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 7, 19)
    name = "2.1-8"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-8; 2.2-16",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x) - (math.tan(x))

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((4.0, 5.0, 1.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((4.0, 4.6, 0.6, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 4.0, "b": 5.0, "c_scale": 1.0, "modified": 0.0}, x=4.3, c=0.0, expected=2.01415212263302
        ),
        FormulaTestCase.value(
            params={"a": 4.0, "b": 5.0, "c_scale": 1.0, "modified": 0.0}, x=4.3, c=0.25, expected=2.7678500693266757
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.0, "b": 5.0, "c_scale": 1.0, "modified": 0.0}, expected=(4.0, 5.0)
        ),
        FormulaTestCase.value(
            params={"a": 4.0, "b": 4.6, "c_scale": 0.6, "modified": 1.0}, x=4.18, c=0.25, expected=2.7994128881553113
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.0, "b": 4.6, "c_scale": 0.6, "modified": 1.0}, expected=(4.0, 4.6)
        ),
    )
