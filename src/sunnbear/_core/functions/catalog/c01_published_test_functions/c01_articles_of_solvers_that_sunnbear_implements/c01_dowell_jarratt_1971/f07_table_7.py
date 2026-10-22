"""This module holds the formula of Table 7 in Dowell, Jarratt (1971).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1971_dowell_jarratt_illinois`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_HASH is a hash of this formula's survey fields; the tests compare it with the survey, so
# that a test fails when the survey changes and this module is not regenerated.
SURVEY_HASH = "748ac0823a89a707"


class DowellJarratt1971Table7(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(n*x - 1)/((n - 1)*x)``, with the parameters ``n = 2, 5, 15, 20``; the formula's interval is
    ``[0.01, 1]``.

    The caption says the y-axis is an asymptote. Starting values `x0 = 0.01`, `x1 = 1.0`.
    """

    number = (1, 1, 1, 7)
    name = "Table 7"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 0.99 * c
        return (n * x - 1) / ((n - 1) * x)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,))),)

    cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.307, c=0.0, expected=-1.2573289902280131),
        FormulaTestCase.value(params={"n": 2.0}, x=0.307, c=0.25, expected=-14.806722689075631),
        FormulaTestCase.value(params={"n": 5.0}, x=0.307, c=0.0, expected=0.4356677524429967),
        FormulaTestCase.value(params={"n": 15.0}, x=0.307, c=0.0, expected=0.8387622149837134),
        FormulaTestCase.value(params={"n": 20.0}, x=0.307, c=0.0, expected=0.8811932110406309),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.01, 1.0)),
    )
