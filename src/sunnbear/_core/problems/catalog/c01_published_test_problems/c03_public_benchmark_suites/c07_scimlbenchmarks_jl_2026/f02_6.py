"""This module holds a formula of SciMLBenchmarks.jl (2026).

The formula comes from the row with the key ``6`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ScimlbenchmarksJl20266(Formula):
    """This formula comes from SciMLBenchmarks.jl (2026).

    The survey writes the source's function as ``sin(20*u) + sin(u) + u - p``, with the parameters ``p = 2.0``; the
    formula's interval is ``[-5.0, 5.0]``.

    comment: High oscillation function
    """

    number = (1, 3, 7, 2)
    name = "6"
    param_names = ("p",)
    source = FormulaSource(
        reference=(
            'SciMLBenchmarks.jl, "Interval Rootfinding Test Suite" by Fabian Gittins (the front matter '
            "of the file), file `benchmarks/IntervalNonlinearProblem/suite.jmd` at commit "
            "`8a67931f726eeb53604926a6dd6bfc750316b4c4`, "
            "https://github.com/SciML/SciMLBenchmarks.jl/blob/8a67931f726eeb53604926a6dd6bfc750316b4c4/benchmarks/IntervalNonlinearProblem/suite.jmd,"
            ' MIT license. The file names no source for its functions; it calls them "a selection of '
            'challenging test functions from the literature".'
        ),
        location="6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return math.sin(20 * x) + math.sin(x) + x - p

    def interval_bounds(self, p: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-5.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("p",), rows=((2.0,),)),)

    test_cases = (
        FormulaTestCase.value(params={"p": 2.0}, x=-2.0, c=0.0, expected=-5.654410587305031),
        FormulaTestCase.value(params={"p": 2.0}, x=-2.0, c=0.25, expected=-6.416466545935461),
        FormulaTestCase.interval_bounds(params={"p": 2.0}, expected=(-5.0, 5.0)),
    )
