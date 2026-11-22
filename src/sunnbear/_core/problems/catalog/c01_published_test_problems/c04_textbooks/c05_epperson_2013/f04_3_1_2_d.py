"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-2(d), 3.1-3(d); 3.2-5(a); 3.3-3(f); Ex. 3.10, 3.12, 3.20; 4.4-3,
4.4-4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013312D(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^6 - x - 1``; the formula's interval is ``[0, 2]``.

    Real roots 1.13472413840152 and -0.77808959867860 (Ex. 3.20). Bisection on `[0, 2]` (3.1); Newton from `x0 = 1`
    (3.2-5, 3.3-3); Durand–Kerner for all 6 roots (Ex. 3.12, Table 3.9); Newton, Halley, super Halley and Chun–Neta from
    `x0 = 2` (Table 3.18) and toward the negative root (Table 3.19); Muller and inverse quadratic interpolation from 0,
    1, 2 (4.4-3, 4.4-4). Ex. 3.10 names it as a polynomial whose deflation leaves a quartic.
    """

    number = (1, 4, 5, 4)
    name = "3.1-2(d)"
    params = ()
    location_in_publication = (
        "Exercises 3.1-2(d), 3.1-3(d), 3.2-5(a), 3.3-3(f); Examples 3.10, 3.12, 3.20; Exercises 4.4-3, 4.4-4"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}^{6} - \tmp{u} - 1",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**6 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-1.553344),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-1.099999),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
