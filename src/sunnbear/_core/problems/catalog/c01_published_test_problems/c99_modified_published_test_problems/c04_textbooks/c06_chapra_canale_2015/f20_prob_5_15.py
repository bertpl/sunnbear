"""This module holds formula f1.99.4.6.20, the modified version of the published formula f1.4.6.20.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.6.20 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChapraCanale2015Prob515(Formula):
    """This formula is the modified version of formula f1.4.6.20, from Chapra, Canale (2015).

    The survey writes the source's function as ``v = sqrt(2*g*H)*tanh(sqrt(2*g*H)/(2*L)*t)``, with the parameters `g =
    9.81` m/s^2, `L = 4` m, `t = 2.5` s, `v = 5` m/s; the published interval is ``[0, 2]``.

    Unknown `H`, the initial head (m) of the cylindrical tank of Fig. P5.15; `L` is the pipe's length and `t` the
    elapsed time. Graphically, and by bisection and false position to `es = 1%`.

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because a shift along x by
    any ``c > 0`` evaluates ``sqrt(2*g*x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 99, 4, 6, 20)
    name = "Prob. 5.15"
    param_names = ("g", "L", "t", "v")
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.15",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, g: float, L: float, t: float, v: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return (v) - (math.sqrt(2 * g * x) * math.tanh(math.sqrt(2 * g * x) / (2 * L) * t)) + c

    def interval_bounds(self, g: float, L: float, t: float, v: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problem."""
        return (ParamTable(names=("g", "L", "t", "v"), rows=((9.81, 4.0, 2.5, 5.0),)),)

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.6, c=0.25, expected=2.5384942505464694
        ),
        FormulaTestCase.value(params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.0, c=-0.25, expected=4.75),
    )
