"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-4`` in the survey of published test problems.
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


class AlefeldPotraShi1993Problem4(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``x^n - a``, with the parameters given per interval, on `[0, 5]`: `a =
    0.2, 1`, `n = 4(2)12`; on `[0.95, 4.05]`: `a = 1`, `n = 8(2)14`; the formula's intervals are `[0, 5]`; `[0.95,
    4.05]`.

    The formula's parameter ``a_`` is the source's ``a``, renamed because ``[a, b]`` names the formula's interval.

    The table pairs each interval with the parameter line beside it. The second interval is printed legibly as `[0.95,
    4.05]`, where Alefeld, Potra, Shi (1995) print `[-0.95, 4.05]`.
    """

    number = (1, 2, 4, 4)
    name = "Problem 4"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("n", latex_symbol="n"),
        FormulaParam("a", latex_symbol=r"x_{\min}"),
        FormulaParam("b", latex_symbol=r"x_{\max}"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 5.1, problem 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{\param{n}} - \param{a_}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "An even power, steep toward the upper bound, with 1 simple root in the lowest 20% of each interval, only "
            "0.05 above the lower bound of the narrower interval."
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
                    (1.0, 8.0, 0.95, 4.05, 3.1),
                    (1.0, 10.0, 0.95, 4.05, 3.1),
                    (1.0, 12.0, 0.95, 4.05, 3.1),
                    (1.0, 14.0, 0.95, 4.05, 3.1),
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
            params={"a_": 1.0, "n": 8.0, "a": 0.95, "b": 4.05, "c_scale": 3.1},
            x=1.88,
            c=0.0,
            expected=155.0496482665168,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 10.0, "a": 0.95, "b": 4.05, "c_scale": 3.1},
            x=1.88,
            c=0.0,
            expected=550.541876833177,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 12.0, "a": 0.95, "b": 4.05, "c_scale": 3.1},
            x=1.88,
            c=0.0,
            expected=1948.3696094791806,
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 14.0, "a": 0.95, "b": 4.05, "c_scale": 3.1},
            x=1.88,
            c=0.0,
            expected=6888.851947743215,
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0, "c_scale": 5.0}, expected=(0.0, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 1.0, "n": 8.0, "a": 0.95, "b": 4.05, "c_scale": 3.1}, expected=(0.95, 4.05)
        ),
    )
