"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.9-8`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson2013398(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``2*sin(pi*x) + x``; the formula's interval is ``[1, 2]``.

    By fixed-point iteration.

    With ``modified = 1``, the interval ``[1, 2]`` becomes ``[1.3, 2]``: its lower bound moves right of the first root,
    near 1.21, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the published interval
    holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 5, 20)
    name = "3.9-8"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.9-8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 2 * math.sin(math.pi * x) + x

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((1.0, 2.0, 1.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((1.3, 2.0, 0.7, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.0, "b": 2.0, "c_scale": 1.0, "modified": 0.0}, x=1.3, c=0.0, expected=-0.31803398874989497
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 2.0, "c_scale": 1.0, "modified": 0.0}, x=1.3, c=0.25, expected=0.737131069919538
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.0, "b": 2.0, "c_scale": 1.0, "modified": 0.0}, expected=(1.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": 1.3, "b": 2.0, "c_scale": 0.7, "modified": 1.0}, x=1.51, c=0.25, expected=-0.40226302887638243
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.3, "b": 2.0, "c_scale": 0.7, "modified": 1.0}, expected=(1.3, 2.0)
        ),
    )
