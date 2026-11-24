"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``Ex. 3 (7.2)`` in the survey of published test problems.
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


class LiZhouLangeTian2026Example3(Formula):
    """This formula comes from Li, Zhou, Lange, Tian (2026).

    The survey writes the source's function as ``p - Phi(x; mu, sigma^2)``, where ``Phi`` is the normal cumulative
    distribution function, with the parameters of Figure 2, ``p = 0.05``, ``mu = 1`` and ``sigma = 1``; the formula's
    interval is ``[-2.5, -0.5]`` (Figure 2).

    Table 3's parameter values (``p = 0.01, 0.9``, ``mu = -2, 2``, ``sigma = 1``) are left out, because the source gives
    them no interval: it draws starting values from ``U(-4, 4)``. Fig. 2 states the root ``-0.6448536``.

    Section 7.2 says that Table 3's experiments seek the root of (7.1), which is a misprint: (7.1) is Section 7.1's
    polynomial, and Section 7.2 sets ``p``, ``mu`` and ``sigma`` and runs eqs. (7.4) and (7.5), which are built from
    this function.
    """

    number = (1, 2, 20, 2)
    name = "Example 3"
    params = (
        FormulaParam(
            "p",
            latex_symbol="p",
            meaning=(
                r"The probability level of the root, which is the $\param{p}$-quantile of the normal distribution with "
                r"mean $\param{mu}$ and standard deviation $\param{sigma}$."
            ),
        ),
        FormulaParam("mu", latex_symbol=r"\mu"),
        FormulaParam("sigma", latex_symbol=r"\sigma"),
    )
    location_in_publication = "Example 3; Section 7.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\param{p} - \frac{1}{2} "
            r"\operatorname{erfc}\left(-\frac{\tmp{u} - \param{mu}}{\param{sigma} \sqrt{2}}\right)"
        ),
        interval="[-2.5, -0.5]",
        summary=(
            r"A decreasing function, flattening below its only root, which is the 5% quantile of a normal distribution "
            r"shifted by $2 \c$."
        ),
        notes=(
            r"The expression equals $$\param{p} - \Phi\left(\frac{\tmp{u} - \param{mu}}{\param{sigma}}\right),$$ with "
            r"$\Phi$ the cumulative distribution function of the standard normal distribution.",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, mu: float, sigma: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return p - 0.5 * math.erfc(-(x - mu) / (sigma * math.sqrt(2)))

    def interval_bounds(self, p: float, mu: float, sigma: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.5, -0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("p", "mu", "sigma"),
                rows=(
                    (
                        0.05,
                        1.0,
                        1.0,
                    ),
                ),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, x=-1.9, c=0.0, expected=0.048134186699615965
        ),
        FormulaTestCase.value(
            params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, x=-1.9, c=0.25, expected=0.04966307073432312
        ),
        FormulaTestCase.interval_bounds(params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, expected=(-2.5, -0.5)),
    )
