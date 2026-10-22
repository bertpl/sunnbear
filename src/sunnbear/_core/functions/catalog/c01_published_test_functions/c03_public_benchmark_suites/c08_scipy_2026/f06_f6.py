"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f6`` in the survey of published test problems. The survey describes this
function in words, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import uniform_noise


class Scipy2026F6(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``random()`` (x > 1); ``-random()`` (x < 1); ``0`` (x = 1); the formula's
    interval is ``[0.5, sqrt(3)]``.

    A formula is a pure function of x, so ``random()`` is ``uniform_noise(x)``, a value in ``[0, 1)`` that depends only
    on x and is distributed as a uniform random draw; the source's cache, which returns the same value for a repeat call
    at the same x, behaves the same way.

    ID original.05.00, the same ID as ``f5``; smoothness -inf; ``random()`` is Python's uniform draw from ``[0, 1)``; no
    derivatives
    """

    number = (1, 3, 8, 6)
    name = "f6"
    param_names = ()
    source = FormulaSource(
        reference=(
            "SciPy 1.18.1, module `scipy/optimize/_tstutils.py`, "
            "https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py. The module cites "
            "2 sources:\n"
            '- [1] Alefeld, G. E., Potra, F. A. and Shi, Y., "Algorithm 748: Enclosing Zeros of '
            'Continuous Functions", ACM Trans. Math. Softw. (1995), '
            "https://dl.acm.org/doi/10.1145/210089.210111\n"
            '- [2] Chandrupatla, T. R., "A new hybrid quadratic/bisection algorithm for finding the '
            'zero of a nonlinear function without using derivatives", Advances in Engineering Software '
            "28.3 (1997): 145-149 (no DOI in the module)"
        ),
        location="f6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.2320508075688772 * c
        if x > 1.0:
            return uniform_noise(x)
        elif x < 1.0:
            return -uniform_noise(x)
        else:
            return 0.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=-0.0187790697131488),
        FormulaTestCase.value(params={}, x=0.869615, c=0.25, expected=-0.56968569810015),
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=0.8392744991175021),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
