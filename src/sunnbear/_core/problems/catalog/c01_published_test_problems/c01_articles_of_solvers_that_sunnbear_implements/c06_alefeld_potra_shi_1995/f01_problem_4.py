"""This module holds a formula of Alefeld, Potra, Shi (1995).

The formula comes from the row with the key ``4`` in the survey of published test problems.
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


class AlefeldPotraShi1995Problem4(Formula):
    """This formula comes from Alefeld, Potra, Shi (1995).

    The survey writes the source's function as ``x^n - a``, with the parameters given per interval, on `[0, 5]`: `a =
    0.2, 1`, `n = 4(2)12`; on `[-0.95, 4.05]`: `a = 1`, `n = 8(2)14`; the formula's intervals are `[0, 5]`; `[-0.95,
    4.05]`.

    The formula's parameter ``a_`` is the source's ``a``, renamed because ``[a, b]`` names the formula's interval.

    Driver problems 15 (`a = 0.2` on `[0, 5]`), 16 (`a = 1` on `[0, 5]`) and 17 (`a = 1` on `[-0.95, 4.05]`).
    """

    number = (1, 1, 6, 1)
    name = "Problem 4"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("n", latex_symbol="n"),
        FormulaParam("a", latex_symbol=r"x_{\min}"),
        FormulaParam("b", latex_symbol=r"x_{\max}"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table I, problem 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{\param{n}} - \param{a_}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An even power with 1 simple root, flat around $\x = 0$ and steep toward the upper bound, both more so for"
            r" larger $\param{n}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, n: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**n - a_

    def interval_bounds(self, a_: float, n: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "n", "a", "b", "c_scale"),
                rows=(
                    (0.2, 4.0, 0.0, 5.0, 5.0),
                    (0.2, 6.0, 0.0, 5.0, 5.0),
                    (0.2, 8.0, 0.0, 5.0, 5.0),
                    (0.2, 10.0, 0.0, 5.0, 5.0),
                    (0.2, 12.0, 0.0, 5.0, 5.0),
                    (1.0, 4.0, 0.0, 5.0, 5.0),
                    (1.0, 6.0, 0.0, 5.0, 5.0),
                    (1.0, 8.0, 0.0, 5.0, 5.0),
                    (1.0, 10.0, 0.0, 5.0, 5.0),
                    (1.0, 12.0, 0.0, 5.0, 5.0),
                    (1.0, 8.0, -0.95, 4.05, 5.0),
                    (1.0, 10.0, -0.95, 4.05, 5.0),
                    (1.0, 12.0, -0.95, 4.05, 5.0),
                    (1.0, 14.0, -0.95, 4.05, 5.0),
                ),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=4.8625
        ),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.25, expected=-0.19609375
        ),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 6.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=11.190625
        ),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 8.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=25.42890625
        ),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 10.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=57.4650390625
        ),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 12.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=129.546337890625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 4.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=4.0625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 6.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=10.390625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 8.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=24.62890625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 10.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=56.6650390625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 12.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=128.746337890625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 8.0, "a": -0.95, "b": 4.05, "c_scale": 5.0},
            x=0.55,
            c=0.0,
            expected=-0.9916266062109375,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 10.0, "a": -0.95, "b": 4.05, "c_scale": 5.0},
            x=0.55,
            c=0.0,
            expected=-0.9974670483788086,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 12.0, "a": -0.95, "b": 4.05, "c_scale": 5.0},
            x=0.55,
            c=0.0,
            expected=-0.9992337821345896,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 14.0, "a": -0.95, "b": 4.05, "c_scale": 5.0},
            x=0.55,
            c=0.0,
            expected=-0.9997682190957133,
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, expected=(0.0, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 1.0, "n": 8.0, "a": -0.95, "b": 4.05, "c_scale": 5.0}, expected=(-0.95, 4.05)
        ),
    )
