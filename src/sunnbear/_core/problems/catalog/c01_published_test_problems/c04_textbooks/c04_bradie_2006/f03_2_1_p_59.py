"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``§2.1 (p. 59); Ex. 2.1–2.3, 2.8, 2.9, 2.11–2.13; Tables 2.1–2.3, 2.5, 2.6;
Fig. 2.1; §2.2 (p. 74); §2.4 (p. 98); 2.1-10; 2.2-10; 2.4-13; 2.5-12 to 2.5-14, 2.5-17`` in the survey of published test
problems.
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


class Bradie200621P59(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^3 + 2*x^2 - 3*x - 1``; the formula's intervals are `(1, 2)`; `(-3,
    -2)`; `(-1, 0)`.

    The chapter's first standard test problem: 3 simple roots, 1 in each interval, among them `1.1986912435` and
    `-2.9122291785`. Bisection with tolerance `5E-5` on `(1, 2)` (Ex. 2.1, 2.2, Table 2.1) and on the other 2 intervals
    (2.1-10); false position on `(1, 2)` and `(-3, -2)` (Ex. 2.3, Tables 2.2, 2.3), and with Aitken extrapolation (Ex.
    2.13); Newton from `p0 = 1, 2, 3` (Ex. 2.8, 2.9, Table 2.6) and from `p0 = -3, -2.5, -2` (Table 2.5, p. 98); secant
    from `p0 = 2, p1 = 1` (Ex. 2.11, 2.12), from `p0 = -2, p1 = -3` (2.5-12) and from the 8 pairs of 2.5-13 and 2.5-14.
    2.2-10, 2.4-13 and 2.5-17 seek the root in `(-1, 0)` to `5E-5`.
    """

    number = (1, 4, 4, 3)
    name = "§2.1 (p. 59)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = (
        "§2.1 (p. 59); Examples 2.1–2.3, 2.8, 2.9, 2.11–2.13; Tables 2.1–2.3, 2.5, 2.6; Fig. 2.1; §2.2 (p."
        " 74); §2.4 (p. 98); Exercises 2.1-10, 2.2-10, 2.4-13, 2.5-12 to 2.5-14, 2.5-17"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3} + 2 \tmp{u}^{2} - 3 \tmp{u} - 1",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 + 2 * x**2 - 3 * x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((1.0, 2.0, 1.0), (-3.0, -2.0, 1.0), (-1.0, 0.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.0, expected=0.6770000000000003),
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.25, expected=-0.7873749999999998),
        FormulaTestCase.value(
            params={"a": -3.0, "b": -2.0, "c_scale": 1.0}, x=-2.7, c=0.0, expected=1.9969999999999986
        ),
        FormulaTestCase.value(params={"a": -1.0, "b": 0.0, "c_scale": 1.0}, x=-0.7, c=0.0, expected=1.7369999999999999),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": -2.0, "c_scale": 1.0}, expected=(-3.0, -2.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 0.0, "c_scale": 1.0}, expected=(-1.0, 0.0)),
    )
