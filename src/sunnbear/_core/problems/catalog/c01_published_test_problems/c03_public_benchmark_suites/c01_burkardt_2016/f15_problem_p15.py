"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p15`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Burkardt2016ProblemP15(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``-abs(x)^(1.0/3.0)*exp(-x^2)`` (x < 0.0); ``0.0`` (x = 0.0);
    ``abs(x)^(1.0/3.0)*exp(-x^2)`` (x > 0.0); the formula's intervals are ``[-10.0, 10.0]`` (rang); ``[-0.25, 0.01]``
    (starts 2 and 1).

    The source's starting points, in order, are ``0.01`` and ``-0.25``.
    """

    number = (1, 3, 1, 15)
    name = "Problem p15"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p15"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"-|\tmp{u}|^{1/3} e^{-\tmp{u}^2} & \text{if } \tmp{u} < 0 \\ "
            r"0 & \text{if } \tmp{u} = 0 \\ "
            r"|\tmp{u}|^{1/3} e^{-\tmp{u}^2} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An odd function with an infinite slope at its root, and below $2 \cdot 10^{-7}$ in magnitude beyond $|\x|"
            r" = 4$ on the wide interval."
        ),
        notes=(
            (
                "The source takes this function from George C. Donovan, Arnold R. Miller and Timothy J. Moreland, "
                '"Pathological Functions for Newton\'s Method", The American Mathematical Monthly 100(1), 53–58 '
                "(1993), https://doi.org/10.1080/00029890.1993.11990365."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x < 0.0:
            return -(abs(x) ** (1.0 / 3.0)) * math.exp(-(x**2))
        elif x == 0.0:
            return 0.0
        else:
            return abs(x) ** (1.0 / 3.0) * math.exp(-(x**2))

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (-0.25, 0.01, 0.26)),
                summary="The published intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-1.7863845473277704e-07
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=-1.3811085133134454e-35, atol=0.0
        ),
        FormulaTestCase.value(
            params={"a": -0.25, "b": 0.01, "c_scale": 0.26}, x=-0.172, c=0.0, expected=-0.5399182170921272
        ),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=0.5, c=0.0, expected=0.6181345911606028
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -0.25, "b": 0.01, "c_scale": 0.26}, expected=(-0.25, 0.01)),
    )
