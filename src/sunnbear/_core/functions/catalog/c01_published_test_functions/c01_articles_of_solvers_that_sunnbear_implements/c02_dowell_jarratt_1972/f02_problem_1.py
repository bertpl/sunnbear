"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Problem 1`` in the survey of published test problems. A script generates
this module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/`
and run `uv run python -m scripts.literature_test_problems.formula_modules 1972_dowell_jarratt_pegasus`; do not edit
this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "fb7c40d9a422068c"


class DowellJarratt1972Problem1(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``(N*x - 1)/((N - 1)*x)``, with the parameters ``N = 2, 10, 20``; the
    formula's interval is ``[0.01, 1]``.

    Starting values `x0 = 0.01`, `x1 = 1.0`. The article chose it to show the slow convergence of Regula Falsi.
    """

    number = (1, 1, 2, 2)
    name = "Problem 1"
    param_names = ("N",)
    source = FormulaSource(
        reference=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an '
            "equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        location="Problem 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, N: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.99 * c
        return (N * x - 1) / ((N - 1) * x)

    def interval_bounds(self, N: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("N",), rows=((2.0,), (10.0,), (20.0,))),)

    cases = (
        FormulaTestCase.value(params={"N": 2.0}, x=0.307, c=0.0, expected=-1.2573289902280131),
        FormulaTestCase.value(params={"N": 2.0}, x=0.307, c=0.25, expected=-14.806722689075631),
        FormulaTestCase.value(params={"N": 10.0}, x=0.307, c=0.0, expected=0.749185667752443),
        FormulaTestCase.value(params={"N": 20.0}, x=0.307, c=0.0, expected=0.8811932110406309),
        FormulaTestCase.interval_bounds(params={"N": 2.0}, expected=(0.01, 1.0)),
    )
