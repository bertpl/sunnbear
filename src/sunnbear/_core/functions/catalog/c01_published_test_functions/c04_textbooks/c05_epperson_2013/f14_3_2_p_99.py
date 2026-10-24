"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.2 (p. 99), Fig. 3.3`` in the survey of published test problems. The
module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson201332P99(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(4/3)*exp(2 - x/2)*(1 + x^-1*log(x))``; the formula's interval is `[0,
    8]` (Fig. 3.3).

    Single root near `x = 0.5`. Newton from `x0` in about `[0.8, 1.2]` gives `x1 < 0`, outside the domain; from `x0 >
    1.2` it grows without bound, where `f -> 0`.

    With ``modified = 1``, the interval starts at ``0.08``, right of 0 by 1% of the published interval's width, rounded
    half up to 1 significant digit; ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new
    interval.

    The published test function fails a benchmark suite's checks of its test functions, because ``log(x)/x`` is not
    finite at ``a = 0``.
    """

    number = (1, 4, 5, 14)
    name = "§3.2 (p. 99)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="§3.2 (p. 99), Fig. 3.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (4 / 3) * math.exp(2 - x / 2) * (1 + x**-1 * math.log(x))

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 8.0, 8.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.08, 8.0, 7.92, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 8.0, "c_scale": 8.0, "modified": 0.0}, x=2.4, c=0.0, expected=4.049827630543694
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 8.0, "c_scale": 8.0, "modified": 0.0}, x=2.4, c=0.25, expected=-10.411256389941297
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 8.0, "c_scale": 8.0, "modified": 0.0}, expected=(0.0, 8.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.08, "b": 8.0, "c_scale": 7.92, "modified": 1.0}, x=2.456, c=0.25, expected=-4.345010769099701
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.08, "b": 8.0, "c_scale": 7.92, "modified": 1.0}, expected=(0.08, 8.0)
        ),
    )
