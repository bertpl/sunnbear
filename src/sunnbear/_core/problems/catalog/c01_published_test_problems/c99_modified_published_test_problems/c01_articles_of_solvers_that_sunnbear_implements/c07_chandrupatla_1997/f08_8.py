"""This module holds formula f1.99.1.7.8, the modified version of the published formula f1.1.7.8.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.7.8 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChandrupatla19978(Formula):
    """This formula is the modified version of formula f1.1.7.8, from Chandrupatla (1997).

    The survey writes the source's function as ``-3062*(1 - xi)*exp(-x)/(xi + (1 - xi)*exp(-x)) - 1013 + 1628/x``, with
    the parameters ``xi = 0.61489``; the published intervals are `[2E-4, 2]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`;
    `[2E-4, 81]`.

    Printed zero: `x = 1.037536`.

    The formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published interval: ``c`` scales x, so
    that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from 0 to 1, the root moves by the
    interval's full width in log scale.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because each interval spans
    orders of magnitude next to the pole of ``1628/x`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 99, 1, 7, 8)
    name = "8"
    param_names = ("xi", "a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, xi: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``."""
        x = x * math.exp(-c * math.log(b / a))
        return -3062 * (1 - xi) * math.exp(-x) / (xi + (1 - xi) * math.exp(-x)) - 1013 + 1628 / x

    def interval_bounds(self, xi: float, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("xi", "a", "b"),
                rows=(
                    (0.61489, 0.0002, 2.0),
                    (0.61489, 0.0002, 3.0),
                    (0.61489, 0.0002, 9.0),
                    (0.61489, 0.0002, 27.0),
                    (0.61489, 0.0002, 81.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0}, x=0.0502377, c=0.25, expected=321870.8552288529
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0}, x=0.0640744, c=0.25, expected=278997.32381392096
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0}, x=0.123868, c=0.25, expected=189238.842524578
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0}, x=0.239458, c=0.25, expected=128136.06406767729
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0}, x=0.462917, c=0.25, expected=86539.74096002016
        ),
    )
