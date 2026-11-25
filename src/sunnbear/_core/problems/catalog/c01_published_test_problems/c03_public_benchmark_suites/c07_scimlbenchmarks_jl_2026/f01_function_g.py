"""This module holds a formula of SciMLBenchmarks.jl (2026).

The formula comes from the row with the key ``g`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ScimlbenchmarksJl2026FunctionG(Formula):
    """This formula comes from SciMLBenchmarks.jl (2026).

    The survey writes the source's function as ``exp(u) - 1e-15``; the formula's interval is ``[-100.0, 0.0]``.

    section "A different function"; the file gives the root as `u = - 15 * log(10)`; the solvers of
    `BracketingNonlinearSolve.jl` call it through `g(u, p) = g(u)`
    """

    number = (1, 3, 7, 1)
    name = "Function g"
    params = ()
    location_in_publication = "Section “A different function”, g"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 100 \c"),),
        expression=r"e^{\tmp{u}} - 10^{-15}",
        interval="[-100, 0]",
        summary=(
            "An exponential minus $10^{-15}$, with 1 root, at most $10^{-15}$ in magnitude below that root, and "
            "constant in floating point at every point more than 37 below that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 100.0 * c
        return math.exp(x) - 1e-15

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-100.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={}, x=-15.0, c=0.0, expected=3.059023195018258e-07),
        FormulaTestCase.value(params={}, x=-70.0, c=0.25, expected=-1e-15, atol=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-100.0, 0.0)),
    )
