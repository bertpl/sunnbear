"""This module holds formula f1.99.1.7.9, the modified version of the published formula f1.1.7.9.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.7.9 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChandrupatla19979(Formula):
    """This formula is the modified version of formula f1.1.7.9, from Chandrupatla (1997).

    The survey writes the source's function as ``exp(x) - 2 - 0.01/x^2 + 0.000002/x^3``; the published intervals are
    `[2E-4, 1]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`; `[2E-4, 81]`.

    Printed zero: `x = 0.7032`.

    The formula holds the test problems on ``[2e-4, 9]`` and wider. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on the published interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c``
    and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problems on ``[2e-4, 9]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0, so that the shift by ``c_scale*c`` at the
    smallest ``c`` that the benchmark suite pipeline tries changes the sign of ``f(a)``.
    """

    number = (1, 99, 1, 7, 9)
    name = "9"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="9",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``."""
        x = x * math.exp(-c * math.log(b / a))
        return math.exp(x) - 2 - 0.01 / x**2 + 0.000002 / x**3

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (0.0002, 9.0),
                    (0.0002, 27.0),
                    (0.0002, 81.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0002, "b": 9.0}, x=0.123868, c=0.25, expected=-135.99740114601173),
        FormulaTestCase.value(params={"a": 0.0002, "b": 27.0}, x=0.239458, c=0.25, expected=-64.03944642544192),
        FormulaTestCase.value(params={"a": 0.0002, "b": 81.0}, x=0.462917, c=0.25, expected=-30.355396483422293),
    )
