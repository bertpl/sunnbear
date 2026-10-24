"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.10(c)`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import bessel_j0, bessel_y0


class Moler2004Ex410C(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``J0(x) = Y0(x)``; the formula's interval is ``[0, 10*pi]``.

    All solutions between 0 and `10*pi`.

    The value ``10*pi`` is rounded to 12 significant digits, the most that a parameter value holds.

    With ``modified = 1``, the interval ``[0, 10*pi]`` becomes ``[2, 10*pi]``: its lower bound moves right of the first
    root, near 1.64, so that ``f(a)`` is finite and the interval holds 9 of the 10 roots.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because ``f(a)`` is not finite,
    since ``bessel_y0(0)`` is ``-inf``, and the interval holds 10 roots, an even number.
    """

    number = (1, 4, 3, 15)
    name = "Ex. 4.10(c)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Ex. 4.10(c)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (bessel_j0(x)) - (bessel_y0(x))

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 31.4159265359, 31.4, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((2.0, 31.4159265359, 29.4, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4, "modified": 0.0},
            x=9.42478,
            c=0.0,
            expected=-0.36726657736486834,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4, "modified": 0.0},
            x=9.42478,
            c=0.25,
            expected=0.05828461127689465,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4, "modified": 0.0}, expected=(0.0, 31.4159265359)
        ),
        FormulaTestCase.value(
            params={"a": 2.0, "b": 31.4159265359, "c_scale": 29.4, "modified": 1.0},
            x=10.8248,
            c=0.25,
            expected=-0.575867514061962,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.0, "b": 31.4159265359, "c_scale": 29.4, "modified": 1.0}, expected=(2.0, 31.4159265359)
        ),
    )
