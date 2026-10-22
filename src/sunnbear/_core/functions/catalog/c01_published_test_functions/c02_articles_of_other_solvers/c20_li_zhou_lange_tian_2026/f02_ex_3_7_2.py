"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``Ex. 3 (7.2)`` in the survey of published test problems. The survey gives
this function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: a normal cumulative distribution function with a mean and a variance. A person therefore writes this module,
and a change of the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class LiZhouLangeTian2026Ex372(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

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
    name = "Ex. 3 (7.2)"
    param_names = ("p", "mu", "sigma")
    source = FormulaSource(
        reference=(
            "Li, X.-J., Zhou, H., Lange, K., Tian, G.-L. (2026). The upper–crossing/solution (US) "
            "algorithm with strongly stable convergence and an acceleration technique for root–finding "
            "problems. Statistics and Computing 36(4), 197. https://doi.org/10.1007/s11222-026-10902-z."
            " Preprint: arXiv 2212.00797v2 (8 November 2025), https://arxiv.org/abs/2212.00797v2. The "
            "authors' R code: https://github.com/Xunjian-Li/US-algorithm.git."
        ),
        location="Ex. 3 (7.2)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, mu: float, sigma: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
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
            ),
        )

    cases = (
        FormulaTestCase.value(
            params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, x=-1.9, c=0.0, expected=0.048134186699615965
        ),
        FormulaTestCase.value(
            params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, x=-1.9, c=0.25, expected=0.04966307073432312
        ),
        FormulaTestCase.interval_bounds(params={"p": 0.05, "mu": 1.0, "sigma": 1.0}, expected=(-2.5, -0.5)),
    )
