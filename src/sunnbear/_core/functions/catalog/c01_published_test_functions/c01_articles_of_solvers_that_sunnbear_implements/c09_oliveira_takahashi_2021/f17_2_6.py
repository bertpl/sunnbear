"""This module holds the formula that Oliveira, Takahashi (2021) labels 2.6.

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class OliveiraTakahashi202126(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``1/(21*x - 1)``, with ``(x != 1/21)`` printed beside it; the formula's
    interval is ``[-1, 1]``.

    The formula returns 0 where the denominator ``21*x - 1`` is 0 in float64, which holds at 2 values of x: the float64
    value of ``1/21`` and the next float64 above it. The authors' code returns 0 only at the first, and divides by 0 at
    the second.
    """

    number = (1, 1, 9, 17)
    name = "2.6"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method "
            "average performance preserving minmax optimality. ACM Transactions on Mathematical "
            "Software 47(1), Article 5. https://doi.org/10.1145/3423597. The article itself is dated "
            "December 2020."
        ),
        location="2.6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        denominator = 21 * x - 1
        if denominator == 0.0:
            return 0.0
        else:
            return 1 / denominator

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.10638297872340426),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.05025125628140703),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
