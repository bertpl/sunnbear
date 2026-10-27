"""This module holds formula f1.99.1.13.4, the modified version of the published formula f1.1.13.4.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.13.4 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026F27(Formula):
    """This formula is the modified version of formula f1.1.13.4, from Ganchovski et al. (2026).

    The survey writes the source's function as ``(81 - p(x)*(108 - p(x)*(54 - p(x)*(12 - p(x)))))*sign(p(x) - 3)``,
    where ``p(x) = x + 1.11111``; the published interval is ``[1, 3]``.

    ``Test Functions.pdf`` prints ``p(x) = x + 1.11``.

    The formula computes the published function, which equals ``(p - 3)**4 * sign(p - 3)``, in the equivalent form
    ``(x - 1.88889)**3 * abs(x - 1.88889)``, on the published interval, and ``c`` shifts x by the rule of category 1,
    with ``c_scale`` the rounded width of the published interval.

    The equivalent form writes the root ``3 - 1.11111`` as the decimal ``1.88889``; float64 rounds ``3 - 1.11111`` and
    ``1.88889`` to the same value, so both forms are 0 at ``x = 1.88889``.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 5e-4 of
    the root; ``(x - 1.88889)**3 * abs(x - 1.88889)`` has no terms that cancel.
    """

    number = (1, 99, 1, 13, 4)
    name = "f27"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f27",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(y - 1.88889)**3 * abs(y - 1.88889)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return (x - 1.88889) ** 3 * abs(x - 1.88889)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
        FormulaTestCase.value(params={}, x=1.6, c=0.25, expected=-0.38731632624146395),
    )
