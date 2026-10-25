"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f27`` in the survey of published test problems. The survey gives this
function as an expression in a helper variable ``p``, defined beside it, not as 1 expression in x, so the module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write it.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a published
test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import sign


class GanchovskiSmithRackauckasTomovTraykov2026F27(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(81 - p(x)*(108 - p(x)*(54 - p(x)*(12 - p(x)))))*sign(p(x) - 3)``,
    where ``p(x) = x + 1.11111``; the formula's interval is ``[1, 3]``.

    ``Test Functions.pdf`` prints ``p(x) = x + 1.11``.

    With ``modified = 1``, the formula computes the published function, which equals ``(p - 3)**4 * sign(p - 3)``, in
    the equivalent form ``(x - 1.88889)**3 * abs(x - 1.88889)``, on the published interval, and ``c`` shifts x as
    category 1 states.

    The equivalent form writes the root ``3 - 1.11111`` as the decimal ``1.88889``; float64 rounds ``3 - 1.11111`` and
    ``1.88889`` to the same value, so both forms are 0 at ``x = 1.88889``.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 5e-4 of
    the root; ``(x - 1.88889)**3 * abs(x - 1.88889)`` has no terms that cancel.
    """

    number = (1, 1, 13, 4)
    name = "f27"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f27",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``(y - 1.88889)**3 * abs(y - 1.88889)``, with ``y = x - c_scale*c``.
        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        if modified == 1:
            return (x - 1.88889) ** 3 * abs(x - 1.88889)
        else:
            p = x + 1.11111
            return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=1.6, c=0.0, expected=-0.006965142972726102),
        FormulaTestCase.value(params={"modified": 0.0}, x=1.6, c=0.25, expected=-0.38731632624146395),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(1.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(1.0, 3.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=1.6, c=0.25, expected=-0.38731632624146395),
    )
