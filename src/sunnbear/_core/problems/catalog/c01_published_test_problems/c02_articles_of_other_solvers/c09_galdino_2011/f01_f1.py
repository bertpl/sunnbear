"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011F1(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's interval is ``[2.5, 3.5]``.

    The appendix states a zero of multiplicity 3 at `x = 3`. The Scilab script of Section IV solves it on `[2.5, 3.5]`.
    """

    number = (1, 2, 9, 1)
    name = "f1"
    params = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="Table IV, f1",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u} + 2\right) \left(\tmp{u} + 1\right) \left(\tmp{u} - 3\right)^{3}",
        interval="[2.5, 3.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.8, c=0.0, expected=-0.14592000000000038),
        FormulaTestCase.value(params={}, x=2.8, c=0.25, expected=-1.4718965625000016),
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.5)),
    )
