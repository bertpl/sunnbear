"""This module holds formula f1.99.3.2.3, the modified version of the published formula f1.3.2.3.

A change of formula f1.3.2.3 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedGsl2024FunctionFunc3(Formula):
    """This formula is the modified version of formula f1.3.2.3, from GSL (2024).

    The survey writes the source's function as ``x^2 - 1e-8``; the published interval is ``[0, 1]``.

    Starting point 1; derivative given

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because its roots ``-1e-4``
    and ``1e-4`` lie ``1e-4`` from ``a = 0``: a shift along x by more than ``1e-4``, in either direction, changes the
    sign of ``f(a)``.

    The modification changes what the test problem tests: the published test problem has its root, ``1e-4``, close to
    the bound ``a = 0`` of an interval of width 1.

    Adding ``c`` moves the root to ``sqrt(1e-8 - c)``, so that the root stays close to ``a`` only for ``c`` near 0; for
    ``c = -0.25``, the root lies near 0.5.
    """

    number = (1, 99, 3, 2, 3)
    name = "Function func3"
    params = ()
    location_in_publication = "test_funcs.c, func3"
    presentation = FormulaPresentation(
        expression=r"\x^{2} - 1.0 \cdot 10^{-8} + \c",
        interval="[0, 1]",
        summary=(
            "A parabola that is negative only within $10^{-4}$ of the lower bound, where the parabola has its minimum, "
            "$-10^{-8}$."
        ),
        notes=(
            (
                r"$\c$ shifts the function along the y-axis, not along x as for the published test "
                r"problem, because its roots, $\pm 10^{-4}$, lie $10^{-4}$ from the lower bound 0, so that "
                "a shift along x by more than $10^{-4}$ changes the function's sign there."
            ),
            (
                "This changes what the test problem tests: the published root lies close to the lower "
                r"bound of a wide interval, while adding $\c$ moves the root to $\sqrt{10^{-8} - \c}$, "
                r"near 0.5 at $\c = -0.25$."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return x**2 - 1e-8 + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.33999999),
        FormulaTestCase.value(params={}, x=0.0, c=-0.25, expected=-0.25000001),
    )
