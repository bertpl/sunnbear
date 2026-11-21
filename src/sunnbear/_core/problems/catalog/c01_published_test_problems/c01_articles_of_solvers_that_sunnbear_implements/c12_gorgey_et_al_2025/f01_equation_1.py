"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaParam, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GorgeyEtAl2025Equation1(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's intervals are `[-2.5, 3]`;
    `[2, 3.5]` (Figure 1's caption and the text below Table 2).

    Roots `-2`, `-1` and `3`; the text names `3` as the root found.
    """

    number = (1, 1, 12, 1)
    name = "Equation 1"
    params = (
        FormulaParam("a"),
        FormulaParam("b"),
        FormulaParam("c_scale"),
    )
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((-2.5, 3.0, 5.5), (2.0, 3.5, 1.5))),)

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5}, x=-0.85, c=0.0, expected=-9.843992812500002
        ),
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5}, x=-0.85, c=0.25, expected=-39.316739150390646
        ),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.5, "c_scale": 1.5}, x=2.45, c=0.0, expected=-2.554272187499998),
        FormulaTestCase.interval_bounds(params={"a": -2.5, "b": 3.0, "c_scale": 5.5}, expected=(-2.5, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.5, "c_scale": 1.5}, expected=(2.0, 3.5)),
    )
