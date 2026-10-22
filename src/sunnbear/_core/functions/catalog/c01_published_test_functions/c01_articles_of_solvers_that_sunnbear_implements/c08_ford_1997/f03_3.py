"""This module holds the formula of 3 in Ford (1997).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1997_ford`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "667b07173ca906c4"


class Ford19973(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``exp(21000/x)/(1.11*10^11*x^2) - 1``; the formula's interval is `[550, 560]`; `[400, 600]`;
    `[350, 850]`.

    Printed root: `x* = 551.77382493033`. The article prints the constant as `21,000`.
    """

    number = (1, 1, 8, 3)
    name = "3"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear "
            "equations. Scientia Iranica 4(1&2), 28–34. The article has no working DOI: the journal's "
            "page, https://scientiairanica.sharif.edu/article_21758.html, lists "
            "10.24200/sci.2020.21758, which doi.org does not resolve. An earlier version is the "
            "University of Essex technical report CSM-257 (1995)."
        ),
        location="3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return math.exp(21000 / x) / (1.11 * 10**11 * x**2) - 1

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
                        550.0,
                        560.0,
                    ),
                    (
                        400.0,
                        600.0,
                    ),
                    (
                        350.0,
                        850.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": 550.0, "b": 560.0}, x=553.0, c=0.0, expected=-0.08499751420971996),
        FormulaTestCase.value(params={"a": 550.0, "b": 560.0}, x=553.0, c=0.25, expected=0.09712049308920227),
        FormulaTestCase.value(params={"a": 400.0, "b": 600.0}, x=460.0, c=0.0, expected=2854.279157641333),
        FormulaTestCase.value(params={"a": 350.0, "b": 850.0}, x=500.0, c=0.0, expected=61.676574469207246),
        FormulaTestCase.interval_bounds(params={"a": 550.0, "b": 560.0}, expected=(550.0, 560.0)),
        FormulaTestCase.interval_bounds(params={"a": 400.0, "b": 600.0}, expected=(400.0, 600.0)),
        FormulaTestCase.interval_bounds(params={"a": 350.0, "b": 850.0}, expected=(350.0, 850.0)),
    )
