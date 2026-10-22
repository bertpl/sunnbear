"""This module holds the formula that Li, Zhou, Lange, Tian (2026) labels 7.1.

The survey gives this function as 1 expression that the script does not translate, with its parameters given as sets
``{a0, a1, a2, a3, m}``, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class LiZhouLangeTian202671(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``a3*theta^m + a2*theta^2 + a1*theta + a0``, with the parameters ``{a0,
    a1, a2, a3, m} = {1, -1, 1, -1, 3}`` and ``{1, -1, -3, 1, 3}``; the formula's interval is ``(0, a)`` with ``a = 2``.

    The formula's x is the source's ``theta``. Eq. (7.1), with ``m >= 3`` real and ``a0 > 0``. The article states the
    roots ``0.4608111`` and ``1`` "for the two cases"; with the printed coefficients, the first case has root ``1`` and
    the second ``0.4608111``. Table 2.
    """

    number = (1, 2, 20, 3)
    name = "7.1"
    param_names = ("a0", "a1", "a2", "a3", "m")
    source = FormulaSource(
        reference=(
            "Li, X.-J., Zhou, H., Lange, K., Tian, G.-L. (2026). The upper–crossing/solution (US) "
            "algorithm with strongly stable convergence and an acceleration technique for root–finding "
            "problems. Statistics and Computing. https://doi.org/10.1007/s11222-026-10902-z. Preprint: "
            "https://arxiv.org/abs/2212.00797. The authors' R code: "
            "https://github.com/Xunjian-Li/US-algorithm.git."
        ),
        location="7.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a0: float, a1: float, a2: float, a3: float, m: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        return a3 * x**m + a2 * x**2 + a1 * x + a0

    def interval_bounds(self, a0: float, a1: float, a2: float, a3: float, m: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a0", "a1", "a2", "a3", "m"),
                rows=(
                    (
                        1.0,
                        -1.0,
                        1.0,
                        -1.0,
                        3.0,
                    ),
                    (
                        1.0,
                        -1.0,
                        -3.0,
                        1.0,
                        3.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, x=0.6, c=0.0, expected=0.544
        ),
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, x=0.6, c=0.25, expected=0.909
        ),
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": -3.0, "a3": 1.0, "m": 3.0}, x=0.6, c=0.0, expected=-0.4639999999999999
        ),
        FormulaTestCase.interval_bounds(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, expected=(0.0, 2.0)
        ),
    )
