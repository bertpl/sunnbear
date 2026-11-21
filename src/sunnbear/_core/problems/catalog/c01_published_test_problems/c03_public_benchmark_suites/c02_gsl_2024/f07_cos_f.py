"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``cos_f`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Gsl2024CosF(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``cos(x)``; the formula's intervals are ``[0, 3], [-3, 0]``.

    Starting points 0.6, -2.5; derivative given
    """

    number = (1, 3, 2, 7)
    name = "cos_f"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="cos_f",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.cos(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((0.0, 3.0, 3.0), (-3.0, 0.0, 3.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, x=0.9, c=0.0, expected=0.6216099682706644),
        FormulaTestCase.value(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, x=0.9, c=0.25, expected=0.9887710779360422),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 0.0, "c_scale": 3.0}, x=-2.1, c=0.0, expected=-0.5048461045998576
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, expected=(0.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": 0.0, "c_scale": 3.0}, expected=(-3.0, 0.0)),
    )
