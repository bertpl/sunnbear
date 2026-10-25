"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``2`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Chandrupatla19972(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``1 - 1/x^2``; the formula's intervals are `[0.5, 1.51]`; `[1E-4, 1E4]`;
    `[1E-6, 1E6]`; `[1E-10, 1E10]`; `[1E-12, 1E12]`.

    Printed zero: `x = 1`. The article says the author proposed it.

    With ``modified = 1``, the formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published
    interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from
    0 to 1, the root moves by the interval's full width in log scale.

    The published test problems on ``[1e-4, 1e4]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0.

    For these intervals, the rounded interval width ``c_scale`` is ``1e4`` or more, so a shift along x by ``c_scale*c``
    takes ``a`` across the pole for every ``c`` above ``1e-8``.
    """

    number = (1, 1, 7, 2)
    name = "2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="2",
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
        return 1 - 1 / x**2

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.5, 1.51, 1.01, 0.0),
                    (0.0001, 10000.0, 10000.0, 0.0),
                    (1e-06, 1000000.0, 1000000.0, 0.0),
                    (1e-10, 10000000000.0, 10000000000.0, 0.0),
                    (1e-12, 1000000000000.0, 1000000000000.0, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0001, 10000.0, 10000.0, 1.0),
                    (1e-06, 1000000.0, 1000000.0, 1.0),
                    (1e-10, 10000000000.0, 10000000000.0, 1.0),
                    (1e-12, 1000000000000.0, 1000000000000.0, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.5, "b": 1.51, "c_scale": 1.01, "modified": 0.0}, x=0.803, c=0.0, expected=-0.5508468399169365
        ),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 1.51, "c_scale": 1.01, "modified": 0.0}, x=0.803, c=0.25, expected=-2.29978279179773
        ),
        FormulaTestCase.value(
            params={"a": 0.0001, "b": 10000.0, "c_scale": 10000.0, "modified": 0.0},
            x=3000.0,
            c=0.0,
            expected=0.9999998888888889,
        ),
        FormulaTestCase.value(
            params={"a": 1e-06, "b": 1000000.0, "c_scale": 1000000.0, "modified": 0.0},
            x=300000.0,
            c=0.0,
            expected=0.9999999999888889,
        ),
        FormulaTestCase.value(
            params={"a": 1e-10, "b": 10000000000.0, "c_scale": 10000000000.0, "modified": 0.0},
            x=3000000000.0,
            c=0.0,
            expected=1.0,
        ),
        FormulaTestCase.value(
            params={"a": 1e-12, "b": 1000000000000.0, "c_scale": 1000000000000.0, "modified": 0.0},
            x=300000000000.0,
            c=0.0,
            expected=1.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.5, "b": 1.51, "c_scale": 1.01, "modified": 0.0}, expected=(0.5, 1.51)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0001, "b": 10000.0, "c_scale": 10000.0, "modified": 0.0}, expected=(0.0001, 10000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-06, "b": 1000000.0, "c_scale": 1000000.0, "modified": 0.0}, expected=(1e-06, 1000000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-10, "b": 10000000000.0, "c_scale": 10000000000.0, "modified": 0.0},
            expected=(1e-10, 10000000000.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-12, "b": 1000000000000.0, "c_scale": 1000000000000.0, "modified": 0.0},
            expected=(1e-12, 1000000000000.0),
        ),
        FormulaTestCase.value(
            params={"a": 0.0001, "b": 10000.0, "c_scale": 10000.0, "modified": 1.0},
            x=6.30957,
            c=0.25,
            expected=-250.18891743125303,
        ),
        FormulaTestCase.value(
            params={"a": 1e-06, "b": 1000000.0, "c_scale": 1000000.0, "modified": 1.0},
            x=15.8489,
            c=0.25,
            expected=-3980.087743782938,
        ),
        FormulaTestCase.value(
            params={"a": 1e-10, "b": 10000000000.0, "c_scale": 10000000000.0, "modified": 1.0},
            x=100.0,
            c=0.25,
            expected=-999999.0000000003,
        ),
        FormulaTestCase.value(
            params={"a": 1e-12, "b": 1000000000000.0, "c_scale": 1000000000000.0, "modified": 1.0},
            x=251.189,
            c=0.25,
            expected=-15848885.893402303,
        ),
    )
