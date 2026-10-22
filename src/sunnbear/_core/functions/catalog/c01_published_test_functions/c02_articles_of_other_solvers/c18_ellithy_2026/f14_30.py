"""This module holds a formula of Ellithy (2026).

The formula comes from the rows with the keys ``30`` and ``31`` in the survey of published test problems. The survey
gives this function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`,
cannot translate: a product written with ``...``. A person therefore writes this module, and a change of the formula's
rows in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Ellithy202630(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints 1 function in 2 rows, each on its own interval:

    - 30: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the formula's interval is ``[0,
      1.5]``
    - 31: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the formula's interval is ``[19,
      21]``

    The function is Wilkinson's polynomial, which the author's file writes out as the product of all 20 factors ``(x -
    1)`` to ``(x - 20)``.
    """

    number = (1, 2, 18, 14)
    name = "30"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="30, 31",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        # the loop multiplies the 20 factors (x - 1) to (x - 20) from the left, in the order of the author's file
        product = x - 1
        for i in range(2, 21):
            product *= x - i
        return product

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (
                        0.0,
                        1.5,
                    ),
                    (
                        19.0,
                        21.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.5}, x=0.45, c=0.0, expected=3.8859900569265306e17),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.5}, x=0.45, c=0.25, expected=1.848893119048187e18),
        FormulaTestCase.value(params={"a": 19.0, "b": 21.0}, x=19.6, c=0.0, expected=-9999185058305838.0),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.5}, expected=(0.0, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": 19.0, "b": 21.0}, expected=(19.0, 21.0)),
    )
