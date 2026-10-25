"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-3(h); 3.2-5(e); 3.3-3(g)`` in the survey of published test problems.
The module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson2013313H(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^2 - sin(x)``; the formula's interval is ``[0, pi]``.

    Bisection to `1E-6`; Newton from `x0 = 1/2`.

    The value ``pi`` is rounded to 12 significant digits, the most that a parameter value holds.

    With ``modified = 1``, the interval ``[0, pi]`` becomes ``[0.03, pi]``: its lower bound moves right of the root at 0
    by 1% of the published interval's width, rounded half up to 1 significant digit.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` is 0 at the
    root ``a = 0``.
    """

    number = (1, 4, 5, 8)
    name = "3.1-3(h)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.1-3(h); 3.2-5(e); 3.3-3(g)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 - math.sin(x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 3.14159265359, 3.14, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.03, 3.14159265359, 3.11, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0},
            x=0.942478,
            c=0.0,
            expected=0.07924766624610098,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0},
            x=0.942478,
            c=0.25,
            expected=-0.1320285948907636,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0}, expected=(0.0, 3.14159265359)
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 3.14159265359, "c_scale": 3.11, "modified": 1.0},
            x=0.963478,
            c=0.25,
            expected=-0.15031994057295994,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.03, "b": 3.14159265359, "c_scale": 3.11, "modified": 1.0}, expected=(0.03, 3.14159265359)
        ),
    )
