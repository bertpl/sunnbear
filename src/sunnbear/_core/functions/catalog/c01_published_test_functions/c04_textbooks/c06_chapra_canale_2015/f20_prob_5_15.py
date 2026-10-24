"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.15`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale2015Prob515(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``v = sqrt(2*g*H)*tanh(sqrt(2*g*H)/(2*L)*t)``, with the parameters `g =
    9.81` m/s^2, `L = 4` m, `t = 2.5` s, `v = 5` m/s; the formula's interval is ``[0, 2]``.

    Unknown `H`, the initial head (m) of the cylindrical tank of Fig. P5.15; `L` is the pipe's length and `t` the
    elapsed time. Graphically, and by bisection and false position to `es = 1%`.

    With ``modified = 1``, the formula keeps the published interval, evaluates the published function at x without
    shifting x, and adds ``c`` to the function's value.

    The published test function fails a benchmark suite's checks of its test functions, because a shift along x by any
    ``c > 0`` evaluates ``sqrt(2*g*x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 4, 6, 20)
    name = "Prob. 5.15"
    param_names = ("g", "L", "t", "v", "modified")
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.15",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, g: float, L: float, t: float, v: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x`` and add ``c``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - 2.0 * c
            f_offset = 0.0
        else:
            f_offset = c
        return (v) - (math.sqrt(2 * g * x) * math.tanh(math.sqrt(2 * g * x) / (2 * L) * t)) + f_offset

    def interval_bounds(self, g: float, L: float, t: float, v: float, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test function."""
        return (
            ParamTable(names=("g", "L", "t", "v", "modified"), rows=((9.81, 4.0, 2.5, 5.0, 0.0),)),
            ParamTable(names=("g", "L", "t", "v", "modified"), rows=((9.81, 4.0, 2.5, 5.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0, "modified": 0.0}, x=0.6, c=0.0, expected=2.2884942505464694
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0, "modified": 0.0}, x=0.6, c=0.25, expected=4.423248410414592
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0, "modified": 1.0},
            x=0.6,
            c=0.25,
            expected=2.5384942505464694,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0, "modified": 1.0}, x=0.0, c=-0.25, expected=4.75
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0, "modified": 0.0}, expected=(0.0, 2.0)
        ),
    )
