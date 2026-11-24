"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``(1.33)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class SuliMayers2003Equation133(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``x = a*x*(1 - x)``, with the parameters `0 < a <= 4`; `a = 3.4, 3.5,
    3.99`; the formula's interval is ``[0, 1]``.

    Fixed points 0 and `1 - 1/a`. For `a = 3.4` the iterates approach a 2-cycle, 0.45 and 0.84, the 2 stable fixed
    points of `g(g(x))` (eq. (1.34)); for `a = 3.5` a 4-cycle; for `a = 3.99`, from `x0 = 0.75`, no regular pattern.
    """

    number = (1, 4, 2, 5)
    name = "Equation (1.33)"
    params = (
        FormulaParam(
            "mu",
            latex_symbol=r"\mu",
            meaning=(
                r"The parameter of the logistic map $\param{mu} \tmp{u} (1 - \tmp{u})$, whose fixed points are the "
                "formula's roots."
            ),
        ),
    )
    location_in_publication = "Eq. (1.33)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} - \param{mu} \tmp{u} \left(1 - \tmp{u}\right)",
        interval="[0, 1]",
        summary=(
            r"A parabola whose roots, the fixed points of the logistic map, lie at $\x = \c$ and $\x = 1 - 1/\param{mu}"
            r" + \c$."
        ),
        notes=(r"$\param{mu}$ is the source's parameter $a$.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, mu: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x) - (mu * x * (1 - x))

    def interval_bounds(self, mu: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("mu",), rows=((3.4,), (3.5,), (3.99,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"mu": 3.4}, x=0.3, c=0.0, expected=-0.414),
        FormulaTestCase.value(params={"mu": 3.4}, x=0.3, c=0.25, expected=-0.11149999999999997),
        FormulaTestCase.value(params={"mu": 3.5}, x=0.3, c=0.0, expected=-0.435),
        FormulaTestCase.value(params={"mu": 3.99}, x=0.3, c=0.0, expected=-0.5379),
        FormulaTestCase.interval_bounds(params={"mu": 3.4}, expected=(0.0, 1.0)),
    )
