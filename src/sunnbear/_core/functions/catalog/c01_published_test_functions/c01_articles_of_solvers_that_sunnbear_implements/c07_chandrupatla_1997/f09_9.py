"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``9`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Chandrupatla19979(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``exp(x) - 2 - 0.01/x^2 + 0.000002/x^3``; the formula's intervals are
    `[2E-4, 1]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`; `[2E-4, 81]`.

    Printed zero: `x = 0.7032`.

    With ``modified = 1``, the formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published
    interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from
    0 to 1, the root moves by the interval's full width in log scale.

    The published test functions on ``[2e-4, 9]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0, so that the shift by ``c_scale*c`` at the
    smallest ``c`` that the conditions test changes the sign of ``f(a)``.
    """

    number = (1, 1, 7, 9)
    name = "9"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="9",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x*exp(-c*ln(b/a))``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - c_scale * c
        else:
            x = x * math.exp(-c * math.log(b / a))
        return math.exp(x) - 2 - 0.01 / x**2 + 0.000002 / x**3

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0002, 1.0, 1.0, 0.0),
                    (0.0002, 3.0, 3.0, 0.0),
                    (0.0002, 9.0, 9.0, 0.0),
                    (0.0002, 27.0, 27.0, 0.0),
                    (0.0002, 81.0, 81.0, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0002, 9.0, 9.0, 1.0),
                    (0.0002, 27.0, 27.0, 1.0),
                    (0.0002, 81.0, 81.0, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 1.0, "c_scale": 1.0, "modified": 0.0},
            x=0.30014,
            c=0.0,
            expected=-0.7608857084494749,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 1.0, "c_scale": 1.0, "modified": 0.0},
            x=0.30014,
            c=0.25,
            expected=-4.9104090962183635,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 3.0, "c_scale": 3.0, "modified": 0.0},
            x=0.90014,
            c=0.0,
            expected=0.44760838287162796,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 0.0},
            x=2.70014,
            c=0.0,
            expected=12.880443534868409,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 0.0},
            x=8.10014,
            c=0.0,
            expected=3292.9291806949154,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 0.0},
            x=24.3001,
            c=0.0,
            expected=35760150646.19565,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 1.0, "c_scale": 1.0, "modified": 0.0}, expected=(0.0002, 1.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 3.0, "c_scale": 3.0, "modified": 0.0}, expected=(0.0002, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 0.0}, expected=(0.0002, 9.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 0.0}, expected=(0.0002, 27.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 0.0}, expected=(0.0002, 81.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 1.0},
            x=0.123868,
            c=0.25,
            expected=-135.99740114601173,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 1.0},
            x=0.239458,
            c=0.25,
            expected=-64.03944642544192,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 1.0},
            x=0.462917,
            c=0.25,
            expected=-30.355396483422293,
        ),
    )
