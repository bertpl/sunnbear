"""This module holds the formula that Stage (2013) labels 3.13.

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Stage2013313(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``0`` if ``x = 0``; ``(1 - 2/3)^-1`` otherwise; the formula's intervals
    are ``[-10, 10]`` (Figure 11); ``[0, 7]`` (text).

    The second branch is a misprint, which the formula implements as the source meant it: ``1/(x - 2/3)``. As printed,
    the branch is the constant 3; the plot title is ``f = 1 / (x - 2/3)``, and the text describes an infinite-magnitude
    discontinuity in place of a root.
    """

    number = (1, 2, 12, 9)
    name = "3.13"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Stage, S. A. (2013). Comments on An Improvement to the Brent's Method. International "
            "Journal of Experimental Algorithms 4(1), 1–16. No DOI; the publisher's PDF: "
            "https://www.cscjournals.org/manuscript/Journals/IJEA/Volume4/Issue1/IJEA-33.pdf."
        ),
        location="3.13",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        if x == 0.0:
            return 0.0
        else:
            return 1 / (x - 2 / 3)

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
                        -10.0,
                        10.0,
                    ),
                    (
                        0.0,
                        7.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.0, expected=-0.21428571428571427),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.25, expected=-0.10344827586206896),
        FormulaTestCase.value(params={"a": 0.0, "b": 7.0}, x=2.1, c=0.0, expected=0.6976744186046511),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 7.0}, expected=(0.0, 7.0)),
    )
