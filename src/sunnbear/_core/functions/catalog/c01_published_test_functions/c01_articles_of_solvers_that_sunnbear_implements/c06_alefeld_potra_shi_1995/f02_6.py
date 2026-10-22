"""This module holds the formula of 6 in Alefeld, Potra, Shi (1995).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1995_alefeld_potra_shi`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "55dda2f8c9abf202"


class AlefeldPotraShi19956(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``2*x*exp(-n) - 2*exp(-n*x) + 1``, with the parameters ``n = 1(1)5, 20(20)100``; the formula's
    interval is ``[0, 1]``.

    Driver problem 19.
    """

    number = (1, 1, 6, 2)
    name = "6"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344. "
            "https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748: "
            "https://www.netlib.org/toms/748."
        ),
        location="6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.0 * c
        return 2 * x * math.exp(-n) - 2 * math.exp(-n * x) + 1

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=((1.0,), (2.0,), (3.0,), (4.0,), (5.0,), (20.0,), (40.0,), (60.0,), (80.0,), (100.0,)),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.2609087766605704),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8656709048842838),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.016422102246085278),
        FormulaTestCase.value(params={"n": 3.0}, x=0.3, c=0.0, expected=0.21673292153952012),
        FormulaTestCase.value(params={"n": 4.0}, x=0.3, c=0.0, expected=0.4086009595088363),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=0.5577824479025916),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.9950424968833594),
        FormulaTestCase.value(params={"n": 40.0}, x=0.3, c=0.0, expected=0.9999877115752933),
        FormulaTestCase.value(params={"n": 60.0}, x=0.3, c=0.0, expected=0.9999999695400406),
        FormulaTestCase.value(params={"n": 80.0}, x=0.3, c=0.0, expected=0.9999999999244973),
        FormulaTestCase.value(params={"n": 100.0}, x=0.3, c=0.0, expected=0.9999999999998128),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
