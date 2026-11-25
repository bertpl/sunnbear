"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-2`` in the survey of published test problems.
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


class AlefeldPotraShi1993Problem2(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``-2*sum((2*i - 5)^2/(x - i^2)^3, i = 1..20)``, with the parameters ``n =
    1(1)19``; the formula's intervals are `[a_n, b_n]` with `a_n = n^2 + 10^(-9)`, `b_n = (n + 1)^2 - 10^(-9)`.

    `n` only selects the interval between the poles at `n^2` and `(n + 1)^2`; `f` has no parameter.
    """

    number = (1, 2, 4, 2)
    name = "Problem 2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 5.1, problem 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"- 2 \sum_{i=1}^{20} \frac{\left(2 i - 5\right)^{2}}{\left(\tmp{u} - i^{2}\right)^{3}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A sum of poles of order 3, with 1 simple root on each published interval, which has a pole just outside "
            "each bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return -2 * (
            ((2 * (1) - 5) ** 2 / (x - (1) ** 2) ** 3)
            + ((2 * (2) - 5) ** 2 / (x - (2) ** 2) ** 3)
            + ((2 * (3) - 5) ** 2 / (x - (3) ** 2) ** 3)
            + ((2 * (4) - 5) ** 2 / (x - (4) ** 2) ** 3)
            + ((2 * (5) - 5) ** 2 / (x - (5) ** 2) ** 3)
            + ((2 * (6) - 5) ** 2 / (x - (6) ** 2) ** 3)
            + ((2 * (7) - 5) ** 2 / (x - (7) ** 2) ** 3)
            + ((2 * (8) - 5) ** 2 / (x - (8) ** 2) ** 3)
            + ((2 * (9) - 5) ** 2 / (x - (9) ** 2) ** 3)
            + ((2 * (10) - 5) ** 2 / (x - (10) ** 2) ** 3)
            + ((2 * (11) - 5) ** 2 / (x - (11) ** 2) ** 3)
            + ((2 * (12) - 5) ** 2 / (x - (12) ** 2) ** 3)
            + ((2 * (13) - 5) ** 2 / (x - (13) ** 2) ** 3)
            + ((2 * (14) - 5) ** 2 / (x - (14) ** 2) ** 3)
            + ((2 * (15) - 5) ** 2 / (x - (15) ** 2) ** 3)
            + ((2 * (16) - 5) ** 2 / (x - (16) ** 2) ** 3)
            + ((2 * (17) - 5) ** 2 / (x - (17) ** 2) ** 3)
            + ((2 * (18) - 5) ** 2 / (x - (18) ** 2) ** 3)
            + ((2 * (19) - 5) ** 2 / (x - (19) ** 2) ** 3)
            + ((2 * (20) - 5) ** 2 / (x - (20) ** 2) ** 3)
        )

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (1.000000001, 3.999999999, 1.0),
                    (4.000000001, 8.999999999, 10.0),
                    (9.000000001, 15.999999999, 10.0),
                    (16.000000001, 24.999999999, 10.0),
                    (25.000000001, 35.999999999, 10.0),
                    (36.000000001, 48.999999999, 10.0),
                    (49.000000001, 63.999999999, 10.0),
                    (64.000000001, 80.999999999, 10.0),
                    (81.000000001, 99.999999999, 10.0),
                    (100.000000001, 120.999999999, 10.0),
                    (121.000000001, 143.999999999, 10.0),
                    (144.000000001, 168.999999999, 10.0),
                    (169.000000001, 195.999999999, 10.0),
                    (196.000000001, 224.999999999, 10.0),
                    (225.000000001, 255.999999999, 10.0),
                    (256.000000001, 288.999999999, 100.0),
                    (289.000000001, 323.999999999, 100.0),
                    (324.000000001, 360.999999999, 100.0),
                    (361.000000001, 399.999999999, 100.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 1.0}, x=1.9, c=0.0, expected=-24.45179770128443
        ),
        FormulaTestCase.value(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 1.0}, x=1.9, c=0.75, expected=-5333.226396309078
        ),
        FormulaTestCase.value(
            params={"a": 4.000000001, "b": 8.999999999, "c_scale": 10.0}, x=5.5, c=0.0, expected=-0.7118000594155782
        ),
        FormulaTestCase.value(
            params={"a": 9.000000001, "b": 15.999999999, "c_scale": 10.0}, x=11.1, c=0.0, expected=-0.0532193077164875
        ),
        FormulaTestCase.value(
            params={"a": 16.000000001, "b": 24.999999999, "c_scale": 10.0}, x=18.7, c=0.0, expected=-0.6891508421777488
        ),
        FormulaTestCase.value(
            params={"a": 25.000000001, "b": 35.999999999, "c_scale": 10.0}, x=28.3, c=0.0, expected=-1.1582276519983778
        ),
        FormulaTestCase.value(
            params={"a": 36.000000001, "b": 48.999999999, "c_scale": 10.0}, x=39.9, c=0.0, expected=-1.4266641633505828
        ),
        FormulaTestCase.value(
            params={"a": 49.000000001, "b": 63.999999999, "c_scale": 10.0}, x=53.5, c=0.0, expected=-1.5643769465075466
        ),
        FormulaTestCase.value(
            params={"a": 64.000000001, "b": 80.999999999, "c_scale": 10.0}, x=69.1, c=0.0, expected=-1.6236996014083958
        ),
        FormulaTestCase.value(
            params={"a": 81.000000001, "b": 99.999999999, "c_scale": 10.0}, x=86.7, c=0.0, expected=-1.6367539271049327
        ),
        FormulaTestCase.value(
            params={"a": 100.000000001, "b": 120.999999999, "c_scale": 10.0},
            x=106.3,
            c=0.0,
            expected=-1.622659500477147,
        ),
        FormulaTestCase.value(
            params={"a": 121.000000001, "b": 143.999999999, "c_scale": 10.0},
            x=127.9,
            c=0.0,
            expected=-1.5928458490473871,
        ),
        FormulaTestCase.value(
            params={"a": 144.000000001, "b": 168.999999999, "c_scale": 10.0},
            x=151.5,
            c=0.0,
            expected=-1.5542307191409745,
        ),
        FormulaTestCase.value(
            params={"a": 169.000000001, "b": 195.999999999, "c_scale": 10.0},
            x=177.1,
            c=0.0,
            expected=-1.511054425185954,
        ),
        FormulaTestCase.value(
            params={"a": 196.000000001, "b": 224.999999999, "c_scale": 10.0},
            x=204.7,
            c=0.0,
            expected=-1.465945256995238,
        ),
        FormulaTestCase.value(
            params={"a": 225.000000001, "b": 255.999999999, "c_scale": 10.0},
            x=234.3,
            c=0.0,
            expected=-1.4205548005209618,
        ),
        FormulaTestCase.value(
            params={"a": 256.000000001, "b": 288.999999999, "c_scale": 100.0},
            x=265.9,
            c=0.0,
            expected=-1.375963293673358,
        ),
        FormulaTestCase.value(
            params={"a": 289.000000001, "b": 323.999999999, "c_scale": 100.0},
            x=299.5,
            c=0.0,
            expected=-1.333012002450678,
        ),
        FormulaTestCase.value(
            params={"a": 324.000000001, "b": 360.999999999, "c_scale": 100.0},
            x=335.1,
            c=0.0,
            expected=-1.292906790485875,
        ),
        FormulaTestCase.value(
            params={"a": 361.000000001, "b": 399.999999999, "c_scale": 100.0},
            x=372.7,
            c=0.0,
            expected=-1.2607251556545698,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 1.0}, expected=(1.000000001, 3.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.000000001, "b": 8.999999999, "c_scale": 10.0}, expected=(4.000000001, 8.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 9.000000001, "b": 15.999999999, "c_scale": 10.0}, expected=(9.000000001, 15.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 16.000000001, "b": 24.999999999, "c_scale": 10.0}, expected=(16.000000001, 24.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 25.000000001, "b": 35.999999999, "c_scale": 10.0}, expected=(25.000000001, 35.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 36.000000001, "b": 48.999999999, "c_scale": 10.0}, expected=(36.000000001, 48.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 49.000000001, "b": 63.999999999, "c_scale": 10.0}, expected=(49.000000001, 63.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 64.000000001, "b": 80.999999999, "c_scale": 10.0}, expected=(64.000000001, 80.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 81.000000001, "b": 99.999999999, "c_scale": 10.0}, expected=(81.000000001, 99.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 100.000000001, "b": 120.999999999, "c_scale": 10.0}, expected=(100.000000001, 120.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 121.000000001, "b": 143.999999999, "c_scale": 10.0}, expected=(121.000000001, 143.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 144.000000001, "b": 168.999999999, "c_scale": 10.0}, expected=(144.000000001, 168.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 169.000000001, "b": 195.999999999, "c_scale": 10.0}, expected=(169.000000001, 195.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 196.000000001, "b": 224.999999999, "c_scale": 10.0}, expected=(196.000000001, 224.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 225.000000001, "b": 255.999999999, "c_scale": 10.0}, expected=(225.000000001, 255.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 256.000000001, "b": 288.999999999, "c_scale": 100.0}, expected=(256.000000001, 288.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 289.000000001, "b": 323.999999999, "c_scale": 100.0}, expected=(289.000000001, 323.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 324.000000001, "b": 360.999999999, "c_scale": 100.0}, expected=(324.000000001, 360.999999999)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 361.000000001, "b": 399.999999999, "c_scale": 100.0}, expected=(361.000000001, 399.999999999)
        ),
    )
