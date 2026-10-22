"""This module holds the formula of Table 4 in Dowell, Jarratt (1971).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1971_dowell_jarratt_illinois`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# The fingerprint of the survey fields that this module is generated from; the tests compare it with
# the survey, so that a module left stale after a change of the survey fails them.
SURVEY_FINGERPRINT = "fedf6c18c727ef0f"


class DowellJarratt1971Table4(Formula):
    """`DowellJarratt1971Table4` evaluates the published function at ``x - (b - a)*c``.

    The source prints ``x^2 - (1 - x)^n``, with the parameters ``n = 2, 5, 15, 20``; the formula's interval is ``[0,
    1]``.

    The caption says the function has 1 inflection point on `[0, 1]`.
    """

    number = (1, 1, 1, 4)
    name = "Table 4"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``."""
        x = x - 1.0 * c
        return x**2 - (1 - x) ** n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,))),)

    cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.25, expected=-0.9),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.07807000000000001),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=0.085252438490057),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.08920207733702387),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
