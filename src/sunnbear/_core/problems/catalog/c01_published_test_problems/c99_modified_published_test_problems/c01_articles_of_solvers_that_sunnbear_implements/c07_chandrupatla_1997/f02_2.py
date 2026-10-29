"""This module holds formula f1.99.1.7.2, the modified version of the published formula f1.1.7.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.7.2 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChandrupatla19972(Formula):
    """This formula is the modified version of formula f1.1.7.2, from Chandrupatla (1997).

    The survey writes the source's function as ``1 - 1/x^2``; the published intervals are `[0.5, 1.51]`; `[1E-4, 1E4]`;
    `[1E-6, 1E6]`; `[1E-10, 1E10]`; `[1E-12, 1E12]`.

    Printed zero: `x = 1`. The article says the author proposed it.

    The formula holds the test problems on ``[1e-4, 1e4]`` and wider. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on the published interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c``
    and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problems on ``[1e-4, 1e4]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0.

    For these intervals, the rounded interval width ``c_scale`` is ``1e4`` or more, so a shift along x by ``c_scale*c``
    takes ``a`` across the pole for every ``c`` above ``1e-8``.

    The widest published interval, ``[1e-12, 1e12]``, becomes ``[1e-12, 1e10]``. On ``[1e-12, 1e12]``, `xtol` scales
    with the interval's width and is about 2, so at the smallest values of ``c`` the root lies within `xtol` of ``a``.

    snuffled's diagnostics then report that all roots lie too close to the interval's edge, and the validation stage
    rejects the test problem with `snuffled_all_roots_too_close_to_edge`. ``1e10`` is the largest power of 10 for ``b``
    at which the root lies farther from ``a`` than the distance at which snuffled reports that diagnostic, a few times
    `xtol`.
    """

    number = (1, 99, 1, 7, 2)
    name = "2"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``."""
        x = x * math.exp(-c * math.log(b / a))
        return 1 - 1 / x**2

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (0.0001, 10000.0),
                    (1e-06, 1000000.0),
                    (1e-10, 10000000000.0),
                    (1e-12, 10000000000.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0001, "b": 10000.0}, x=6.30957, c=0.25, expected=-250.18891743125303),
        FormulaTestCase.value(params={"a": 1e-06, "b": 1000000.0}, x=15.8489, c=0.25, expected=-3980.087743782938),
        FormulaTestCase.value(params={"a": 1e-10, "b": 10000000000.0}, x=100.0, c=0.25, expected=-999999.0000000003),
        FormulaTestCase.value(params={"a": 1e-12, "b": 10000000000.0}, x=251.189, c=0.25, expected=-1584887.6893402336),
    )
