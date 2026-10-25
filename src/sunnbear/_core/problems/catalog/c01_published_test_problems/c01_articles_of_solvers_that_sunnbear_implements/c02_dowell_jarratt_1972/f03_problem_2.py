"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Problem 2`` in the survey of published test problems. A script generates
this module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/`
and run `uv run python -m scripts.literature_test_problems.formula_modules 1972_dowell_jarratt_pegasus`; do not edit
this file.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import bessel_j0, bessel_j1, bessel_y0, bessel_y1

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "ec66590e86154058"


class DowellJarratt1972Problem2(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``J0(K)*Y1(K*x) - J1(K*x)*Y0(K)``, with the parameters ``K = 2.5, 3.0``;
    the formula's interval is ``[0.1, 1]``.

    Starting values `x0 = 0.1`, `x1 = 1.0`. Roots `0.149436` for `K = 2.5` and `0.370989` for `K = 3.0`. The article
    does not define `J` and `Y`; they read as the Bessel functions of the first and second kind. The article says the
    problem arises in nuclear reactor theory.
    """

    number = (1, 1, 2, 3)
    name = "Problem 2"
    param_names = ("K",)
    source = FormulaSource(
        reference=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an '
            "equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        location="Problem 2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, K: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.9 * c
        return bessel_j0(K) * bessel_y1(K * x) - bessel_j1(K * x) * bessel_y0(K)

    def interval_bounds(self, K: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("K",), rows=((2.5,), (3.0,))),)

    test_cases = (
        FormulaTestCase.value(params={"K": 2.5}, x=0.37, c=0.0, expected=-0.16549921993513564),
        FormulaTestCase.value(params={"K": 2.5}, x=0.37, c=0.25, expected=0.0050575863514413745),
        FormulaTestCase.value(params={"K": 3.0}, x=0.37, c=0.0, expected=0.0009313171849989814),
        FormulaTestCase.interval_bounds(params={"K": 2.5}, expected=(0.1, 1.0)),
    )
