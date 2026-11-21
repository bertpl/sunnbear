"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(f)`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016236F(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sin(x) - exp(-x)``; the formula's intervals are `[0, 1]`; `[3, 4]`;
    `[6, 7]`.

    As 2.3-6(a).
    """

    number = (1, 4, 7, 38)
    name = "2.3-6(f)"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.3-6(f)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(x) - math.exp(-x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((0.0, 1.0, 1.0), (3.0, 4.0, 1.0), (6.0, 7.0, 1.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-0.44529801402037833),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=-0.9012502552300357),
        FormulaTestCase.value(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=-0.19462886154448822),
        FormulaTestCase.value(params={"a": 6.0, "b": 7.0, "c_scale": 1.0}, x=6.3, c=0.0, expected=0.014977595707320806),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": 6.0, "b": 7.0, "c_scale": 1.0}, expected=(6.0, 7.0)),
    )
