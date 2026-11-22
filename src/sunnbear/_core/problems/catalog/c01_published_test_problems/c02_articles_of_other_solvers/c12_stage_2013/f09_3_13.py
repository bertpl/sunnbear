"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.13`` in the survey of published test problems.
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


class Stage2013313(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``0`` if ``x = 0``; ``(1 - 2/3)^-1`` otherwise; the formula's intervals
    are ``[-10, 10]`` (Figure 11); ``[0, 7]`` (text).

    Both branches are misprints, which the formula implements as the source meant them: ``0`` where ``x - 2/3`` is
    ``0``, and ``1/(x - 2/3)`` otherwise.

    - **The second branch:** as printed, it is the constant 3; the plot title is ``f = 1 / (x - 2/3)``, and the text
      describes an infinite-magnitude discontinuity in place of a root.
    - **The first branch:** as printed, ``0`` at ``x = 0`` makes ``x = 0`` a root, the first bisection midpoint of
      ``[-10, 10]`` and a bound of ``[0, 7]``. That contradicts §3.2, whose roots are not exact bisection points, the
      text, which says that on ``(0,7)`` only Brent's method stumbles into the root, and Figure 11, where bisection
      needs about 57 calls. The formula reads the branch as ``0`` at the pole ``x = 2/3``, which the article does not
      print but which lets a method that lands exactly on the pole stop there.
    """

    number = (1, 2, 12, 9)
    name = "3.13"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§3.13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } \tmp{u} - 2/3 = 0 \\ "
            r"\frac{1}{\tmp{u} - 2/3} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        d = x - 2 / 3
        if d == 0.0:
            return 0.0
        else:
            return 1 / d

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (0.0, 7.0, 7.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-0.21428571428571427
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=-0.10344827586206896
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 7.0, "c_scale": 7.0}, x=2.1, c=0.0, expected=0.6976744186046511),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=0.0, c=0.0, expected=-1.5),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=0.6666666666666666, c=0.0, expected=0.0
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 7.0, "c_scale": 7.0}, expected=(0.0, 7.0)),
    )
