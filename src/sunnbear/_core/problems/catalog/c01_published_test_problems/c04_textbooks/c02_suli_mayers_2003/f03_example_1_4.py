"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``Example 1.4`` in the survey of published test problems.
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


class SuliMayers2003Example14(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``x = g(x)``, with ``g(x) = 2^(-(1 + log2(1/x)^(1/alpha))^alpha)`` for
    ``0 < x <= 1`` and ``g(0) = 0``, with the parameters ``alpha > 0``; ``alpha = 1/2, 1, 2`` (Fig. 1.3); the formula's
    interval is ``[0, 1]``.

    Fixed point 0. From ``x0 = 1``, ``x_k = 2^(-k^alpha)``: sublinear for ``alpha < 1``, linear for ``alpha = 1``,
    superlinear for ``alpha > 1``.

    The formula is the difference form ``x - g(x)`` of the fixed-point equation ``x = g(x)``.
    """

    number = (1, 4, 2, 3)
    name = "Example 1.4"
    params = (
        FormulaParam(
            "alpha",
            latex_symbol=r"\alpha",
            meaning=(
                r"The exponent of $k$ in the terms $2^{-k^{\param{alpha}}}$ for $k = 0, 1, 2, \ldots$; $\fn{g}$ maps "
                "each term to the next."
            ),
        ),
    )
    location_in_publication = "Example 1.4"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \c"),
            (
                r"\fn{g}(\x)",
                r"2^{-\left(1 + \left(\log_2\left(\frac{1}{\x}\right)\right)^{1/\param{alpha}}\right)^{\param{alpha}}}",
            ),
        ),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } \tmp{u} = 0 \\ "
            r"\tmp{u} - \fn{g}(\tmp{u}) & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 1]",
        summary=(
            r"A function with its only root at $\x = \c$, where the slope is 0 for $\param{alpha} = 1/2$, $1/2$ for "
            r"$\param{alpha} = 1$ and 1 for $\param{alpha} = 2$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, alpha: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        # the formula is the difference form x - g(x) of the fixed-point equation x = g(x), with g(0) = 0
        if x == 0.0:
            return 0.0
        else:
            return x - 2.0 ** -math.pow(1.0 + math.pow(math.log2(1.0 / x), 1.0 / alpha), alpha)

    def interval_bounds(self, alpha: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("alpha",), rows=((0.5,), (1.0,), (2.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"alpha": 0.5}, x=0.3, c=0.0, expected=0.05073673914100621),
        FormulaTestCase.value(params={"alpha": 0.5}, x=0.3, c=0.25, expected=0.003804662178248523),
        FormulaTestCase.value(params={"alpha": 1.0}, x=0.3, c=0.0, expected=0.15),
        FormulaTestCase.value(params={"alpha": 2.0}, x=0.3, c=0.0, expected=0.2758669411995428),
        FormulaTestCase.value(params={"alpha": 0.5}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"alpha": 0.5}, expected=(0.0, 1.0)),
    )
