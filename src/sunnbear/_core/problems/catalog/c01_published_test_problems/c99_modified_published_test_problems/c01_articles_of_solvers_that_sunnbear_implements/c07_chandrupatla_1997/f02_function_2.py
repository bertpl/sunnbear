"""This module holds formula f1.99.1.7.2, the modified version of the published formula f1.1.7.2.

A change of formula f1.1.7.2 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ModifiedChandrupatla1997Function2(Formula):
    """This formula is the modified version of formula f1.1.7.2, from Chandrupatla (1997).

    The survey writes the source's function as ``1 - 1/x^2``; the published intervals are `[0.5, 1.51]`; `[1E-4, 1E4]`;
    `[1E-6, 1E6]`; `[1E-10, 1E10]`; `[1E-12, 1E12]`.

    Printed zero: `x = 1`. The article says the author proposed it.

    The formula holds the test problems on ``[1e-4, 1e4]`` and wider. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on its interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c``
    and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problems on ``[1e-4, 1e4]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0.

    For these intervals, the rounded interval width ``c_scale`` is ``1e4`` or more, so a shift along x by ``c_scale*c``
    takes ``a`` across the pole for every ``c`` above ``1e-8``.

    The widest published interval, ``[1e-12, 1e12]``, becomes ``[1e-12, 1e10]``. On ``[1e-12, 1e12]``, `xtol` scales
    with the interval's width and is about 2. The root lies at ``(b/a)**c``, which is 1 at ``c = 0``, so at the smallest
    values of ``c`` the root lies within `xtol` of ``a``.

    snuffled's diagnostics report that all roots lie too close to the interval's edge when they lie within a few times
    `xtol` of a bound, and the validation stage then rejects the test problem with
    `snuffled_all_roots_too_close_to_edge`.

    ``1e10`` is the largest power of 10 for ``b`` at which the root stays more than a few times `xtol` from ``a``.
    """

    number = (1, 99, 1, 7, 2)
    name = "Function 2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
    )
    location_in_publication = "Table 1, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x e^{-\c \ln(\param{b}/\param{a})}"),),
        expression=r"1 - \frac{1}{\tmp{u}^{2}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An increasing function with 1 root, steep near the lower bound because of a pole at $\x = 0$, and within "
            r"0.01 of 1 above $\x = 10$."
        ),
        notes=(
            (
                r"$\c$ scales x, so that the root moves by the factor $(\param{b}/\param{a})^{\c}$ and "
                "never reaches 0: the interval spans orders of magnitude next to the pole at 0, and a "
                "shift along x would move the lower bound across it."
            ),
            (
                "The widest published interval, $[10^{-12}, 10^{12}]$, becomes $[10^{-12}, 10^{10}]$, "
                "because the benchmark's tolerance on x is a fixed fraction of the interval's width."
            ),
            (
                "On the published interval that tolerance is about 2, so that at the smallest values of "
                r"$\c$ the root, near 1, lies within that tolerance of the lower bound, closer than the "
                "benchmark suite inclusion conditions allow."
            ),
        ),
    )
    effect_of_c = EffectOfC.SCALES_X

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
                summary=(
                    "The published intervals $[10^{-4}, 10^{4}]$ and wider, "
                    "with the widest narrowed to $[10^{-12}, 10^{10}]$."
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0001, "b": 10000.0}, x=6.30957, c=0.25, expected=-250.18891743125303),
        FormulaTestCase.value(params={"a": 1e-06, "b": 1000000.0}, x=15.8489, c=0.25, expected=-3980.087743782938),
        FormulaTestCase.value(params={"a": 1e-10, "b": 10000000000.0}, x=100.0, c=0.25, expected=-999999.0000000003),
        FormulaTestCase.value(params={"a": 1e-12, "b": 10000000000.0}, x=251.189, c=0.25, expected=-1584887.6893402336),
    )
