"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-2`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class AlefeldPotraShi1993T512(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``-2*sum((2*i - 5)^2/(x - i^2)^3, i = 1..20)``, with the parameters ``n =
    1(1)19``; the formula's intervals are `[a_n, b_n]` with `a_n = n^2 + 10^(-9)`, `b_n = (n + 1)^2 - 10^(-9)`.

    `n` only selects the interval between the poles at `n^2` and `(n + 1)^2`; `f` has no parameter.

    With ``modified = 1``, each bound moves away from its pole, at ``n^2`` or ``(n + 1)^2``, to a distance of 1% of the
    published interval's width, rounded half up to 1 significant digit, such as ``[1.03, 3.97]`` for ``n = 1``.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because each bound lies
    ``1e-9`` from a pole, so that a shift along x by more than ``1e-9`` crosses it.
    """

    number = (1, 2, 4, 2)
    name = "T5.1-2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear "
            "equations. Mathematics of Computation 61(204), 733–744. "
            "https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        location="T5.1-2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
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

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (1.000000001, 3.999999999, 3.0, 0.0),
                    (4.000000001, 8.999999999, 5.0, 0.0),
                    (9.000000001, 15.999999999, 7.0, 0.0),
                    (16.000000001, 24.999999999, 9.0, 0.0),
                    (25.000000001, 35.999999999, 11.0, 0.0),
                    (36.000000001, 48.999999999, 13.0, 0.0),
                    (49.000000001, 63.999999999, 15.0, 0.0),
                    (64.000000001, 80.999999999, 17.0, 0.0),
                    (81.000000001, 99.999999999, 19.0, 0.0),
                    (100.000000001, 120.999999999, 21.0, 0.0),
                    (121.000000001, 143.999999999, 23.0, 0.0),
                    (144.000000001, 168.999999999, 25.0, 0.0),
                    (169.000000001, 195.999999999, 27.0, 0.0),
                    (196.000000001, 224.999999999, 29.0, 0.0),
                    (225.000000001, 255.999999999, 31.0, 0.0),
                    (256.000000001, 288.999999999, 33.0, 0.0),
                    (289.000000001, 323.999999999, 35.0, 0.0),
                    (324.000000001, 360.999999999, 37.0, 0.0),
                    (361.000000001, 399.999999999, 39.0, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (1.03, 3.97, 2.94, 1.0),
                    (4.05, 8.95, 4.9, 1.0),
                    (9.07, 15.93, 6.86, 1.0),
                    (16.09, 24.91, 8.82, 1.0),
                    (25.1, 35.9, 10.8, 1.0),
                    (36.1, 48.9, 12.8, 1.0),
                    (49.2, 63.8, 14.6, 1.0),
                    (64.2, 80.8, 16.6, 1.0),
                    (81.2, 99.8, 18.6, 1.0),
                    (100.2, 120.8, 20.6, 1.0),
                    (121.2, 143.8, 22.6, 1.0),
                    (144.3, 168.7, 24.4, 1.0),
                    (169.3, 195.7, 26.4, 1.0),
                    (196.3, 224.7, 28.4, 1.0),
                    (225.3, 255.7, 30.4, 1.0),
                    (256.3, 288.7, 32.4, 1.0),
                    (289.4, 323.6, 34.2, 1.0),
                    (324.4, 360.6, 36.2, 1.0),
                    (361.4, 399.6, 38.2, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 3.0, "modified": 0.0},
            x=1.9,
            c=0.0,
            expected=-24.45179770128443,
        ),
        FormulaTestCase.value(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 3.0, "modified": 0.0},
            x=1.9,
            c=0.25,
            expected=-5333.226396309078,
        ),
        FormulaTestCase.value(
            params={"a": 4.000000001, "b": 8.999999999, "c_scale": 5.0, "modified": 0.0},
            x=5.5,
            c=0.0,
            expected=-0.7118000594155782,
        ),
        FormulaTestCase.value(
            params={"a": 9.000000001, "b": 15.999999999, "c_scale": 7.0, "modified": 0.0},
            x=11.1,
            c=0.0,
            expected=-0.0532193077164875,
        ),
        FormulaTestCase.value(
            params={"a": 16.000000001, "b": 24.999999999, "c_scale": 9.0, "modified": 0.0},
            x=18.7,
            c=0.0,
            expected=-0.6891508421777488,
        ),
        FormulaTestCase.value(
            params={"a": 25.000000001, "b": 35.999999999, "c_scale": 11.0, "modified": 0.0},
            x=28.3,
            c=0.0,
            expected=-1.1582276519983778,
        ),
        FormulaTestCase.value(
            params={"a": 36.000000001, "b": 48.999999999, "c_scale": 13.0, "modified": 0.0},
            x=39.9,
            c=0.0,
            expected=-1.4266641633505828,
        ),
        FormulaTestCase.value(
            params={"a": 49.000000001, "b": 63.999999999, "c_scale": 15.0, "modified": 0.0},
            x=53.5,
            c=0.0,
            expected=-1.5643769465075466,
        ),
        FormulaTestCase.value(
            params={"a": 64.000000001, "b": 80.999999999, "c_scale": 17.0, "modified": 0.0},
            x=69.1,
            c=0.0,
            expected=-1.6236996014083958,
        ),
        FormulaTestCase.value(
            params={"a": 81.000000001, "b": 99.999999999, "c_scale": 19.0, "modified": 0.0},
            x=86.7,
            c=0.0,
            expected=-1.6367539271049327,
        ),
        FormulaTestCase.value(
            params={"a": 100.000000001, "b": 120.999999999, "c_scale": 21.0, "modified": 0.0},
            x=106.3,
            c=0.0,
            expected=-1.622659500477147,
        ),
        FormulaTestCase.value(
            params={"a": 121.000000001, "b": 143.999999999, "c_scale": 23.0, "modified": 0.0},
            x=127.9,
            c=0.0,
            expected=-1.5928458490473871,
        ),
        FormulaTestCase.value(
            params={"a": 144.000000001, "b": 168.999999999, "c_scale": 25.0, "modified": 0.0},
            x=151.5,
            c=0.0,
            expected=-1.5542307191409745,
        ),
        FormulaTestCase.value(
            params={"a": 169.000000001, "b": 195.999999999, "c_scale": 27.0, "modified": 0.0},
            x=177.1,
            c=0.0,
            expected=-1.511054425185954,
        ),
        FormulaTestCase.value(
            params={"a": 196.000000001, "b": 224.999999999, "c_scale": 29.0, "modified": 0.0},
            x=204.7,
            c=0.0,
            expected=-1.465945256995238,
        ),
        FormulaTestCase.value(
            params={"a": 225.000000001, "b": 255.999999999, "c_scale": 31.0, "modified": 0.0},
            x=234.3,
            c=0.0,
            expected=-1.4205548005209618,
        ),
        FormulaTestCase.value(
            params={"a": 256.000000001, "b": 288.999999999, "c_scale": 33.0, "modified": 0.0},
            x=265.9,
            c=0.0,
            expected=-1.375963293673358,
        ),
        FormulaTestCase.value(
            params={"a": 289.000000001, "b": 323.999999999, "c_scale": 35.0, "modified": 0.0},
            x=299.5,
            c=0.0,
            expected=-1.333012002450678,
        ),
        FormulaTestCase.value(
            params={"a": 324.000000001, "b": 360.999999999, "c_scale": 37.0, "modified": 0.0},
            x=335.1,
            c=0.0,
            expected=-1.292906790485875,
        ),
        FormulaTestCase.value(
            params={"a": 361.000000001, "b": 399.999999999, "c_scale": 39.0, "modified": 0.0},
            x=372.7,
            c=0.0,
            expected=-1.2607251556545698,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.000000001, "b": 3.999999999, "c_scale": 3.0, "modified": 0.0},
            expected=(1.000000001, 3.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.000000001, "b": 8.999999999, "c_scale": 5.0, "modified": 0.0},
            expected=(4.000000001, 8.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 9.000000001, "b": 15.999999999, "c_scale": 7.0, "modified": 0.0},
            expected=(9.000000001, 15.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 16.000000001, "b": 24.999999999, "c_scale": 9.0, "modified": 0.0},
            expected=(16.000000001, 24.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 25.000000001, "b": 35.999999999, "c_scale": 11.0, "modified": 0.0},
            expected=(25.000000001, 35.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 36.000000001, "b": 48.999999999, "c_scale": 13.0, "modified": 0.0},
            expected=(36.000000001, 48.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 49.000000001, "b": 63.999999999, "c_scale": 15.0, "modified": 0.0},
            expected=(49.000000001, 63.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 64.000000001, "b": 80.999999999, "c_scale": 17.0, "modified": 0.0},
            expected=(64.000000001, 80.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 81.000000001, "b": 99.999999999, "c_scale": 19.0, "modified": 0.0},
            expected=(81.000000001, 99.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 100.000000001, "b": 120.999999999, "c_scale": 21.0, "modified": 0.0},
            expected=(100.000000001, 120.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 121.000000001, "b": 143.999999999, "c_scale": 23.0, "modified": 0.0},
            expected=(121.000000001, 143.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 144.000000001, "b": 168.999999999, "c_scale": 25.0, "modified": 0.0},
            expected=(144.000000001, 168.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 169.000000001, "b": 195.999999999, "c_scale": 27.0, "modified": 0.0},
            expected=(169.000000001, 195.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 196.000000001, "b": 224.999999999, "c_scale": 29.0, "modified": 0.0},
            expected=(196.000000001, 224.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 225.000000001, "b": 255.999999999, "c_scale": 31.0, "modified": 0.0},
            expected=(225.000000001, 255.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 256.000000001, "b": 288.999999999, "c_scale": 33.0, "modified": 0.0},
            expected=(256.000000001, 288.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 289.000000001, "b": 323.999999999, "c_scale": 35.0, "modified": 0.0},
            expected=(289.000000001, 323.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 324.000000001, "b": 360.999999999, "c_scale": 37.0, "modified": 0.0},
            expected=(324.000000001, 360.999999999),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 361.000000001, "b": 399.999999999, "c_scale": 39.0, "modified": 0.0},
            expected=(361.000000001, 399.999999999),
        ),
        FormulaTestCase.value(
            params={"a": 1.03, "b": 3.97, "c_scale": 2.94, "modified": 1.0},
            x=1.912,
            c=0.25,
            expected=-3245.921784746983,
        ),
        FormulaTestCase.value(
            params={"a": 4.05, "b": 8.95, "c_scale": 4.9, "modified": 1.0}, x=5.52, c=0.25, expected=-78.36316187459528
        ),
        FormulaTestCase.value(
            params={"a": 9.07, "b": 15.93, "c_scale": 6.86, "modified": 1.0},
            x=11.128,
            c=0.25,
            expected=-28.3452146369843,
        ),
        FormulaTestCase.value(
            params={"a": 16.09, "b": 24.91, "c_scale": 8.82, "modified": 1.0},
            x=18.736,
            c=0.25,
            expected=-120.12748402260388,
        ),
        FormulaTestCase.value(
            params={"a": 25.1, "b": 35.9, "c_scale": 10.8, "modified": 1.0},
            x=28.34,
            c=0.25,
            expected=-190.6464124364607,
        ),
        FormulaTestCase.value(
            params={"a": 36.1, "b": 48.9, "c_scale": 12.8, "modified": 1.0},
            x=39.94,
            c=0.25,
            expected=-241.7666581280263,
        ),
        FormulaTestCase.value(
            params={"a": 49.2, "b": 63.8, "c_scale": 14.6, "modified": 1.0},
            x=53.58,
            c=0.25,
            expected=-201.33743333034084,
        ),
        FormulaTestCase.value(
            params={"a": 64.2, "b": 80.8, "c_scale": 16.6, "modified": 1.0},
            x=69.18,
            c=0.25,
            expected=-221.40818669786006,
        ),
        FormulaTestCase.value(
            params={"a": 81.2, "b": 99.8, "c_scale": 18.6, "modified": 1.0},
            x=86.78,
            c=0.25,
            expected=-234.2023727016661,
        ),
        FormulaTestCase.value(
            params={"a": 100.2, "b": 120.8, "c_scale": 20.6, "modified": 1.0},
            x=106.38,
            c=0.25,
            expected=-241.78013013008834,
        ),
        FormulaTestCase.value(
            params={"a": 121.2, "b": 143.8, "c_scale": 22.6, "modified": 1.0},
            x=127.98,
            c=0.25,
            expected=-245.6439159946042,
        ),
        FormulaTestCase.value(
            params={"a": 144.3, "b": 168.7, "c_scale": 24.4, "modified": 1.0},
            x=151.62,
            c=0.25,
            expected=-205.55688252354955,
        ),
        FormulaTestCase.value(
            params={"a": 169.3, "b": 195.7, "c_scale": 26.4, "modified": 1.0},
            x=177.22,
            c=0.25,
            expected=-207.42303764882604,
        ),
        FormulaTestCase.value(
            params={"a": 196.3, "b": 224.7, "c_scale": 28.4, "modified": 1.0},
            x=204.82,
            c=0.25,
            expected=-207.89309828829218,
        ),
        FormulaTestCase.value(
            params={"a": 225.3, "b": 255.7, "c_scale": 30.4, "modified": 1.0},
            x=234.42,
            c=0.25,
            expected=-207.31984414032246,
        ),
        FormulaTestCase.value(
            params={"a": 256.3, "b": 288.7, "c_scale": 32.4, "modified": 1.0},
            x=266.02,
            c=0.25,
            expected=-205.9698269587908,
        ),
        FormulaTestCase.value(
            params={"a": 289.4, "b": 323.6, "c_scale": 34.2, "modified": 1.0},
            x=299.66,
            c=0.25,
            expected=-179.0296896097693,
        ),
        FormulaTestCase.value(
            params={"a": 324.4, "b": 360.6, "c_scale": 36.2, "modified": 1.0},
            x=335.26,
            c=0.25,
            expected=-178.04540523008717,
        ),
        FormulaTestCase.value(
            params={"a": 361.4, "b": 399.6, "c_scale": 38.2, "modified": 1.0},
            x=372.86,
            c=0.25,
            expected=-176.68235557293022,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.03, "b": 3.97, "c_scale": 2.94, "modified": 1.0}, expected=(1.03, 3.97)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.05, "b": 8.95, "c_scale": 4.9, "modified": 1.0}, expected=(4.05, 8.95)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 9.07, "b": 15.93, "c_scale": 6.86, "modified": 1.0}, expected=(9.07, 15.93)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 16.09, "b": 24.91, "c_scale": 8.82, "modified": 1.0}, expected=(16.09, 24.91)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 25.1, "b": 35.9, "c_scale": 10.8, "modified": 1.0}, expected=(25.1, 35.9)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 36.1, "b": 48.9, "c_scale": 12.8, "modified": 1.0}, expected=(36.1, 48.9)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 49.2, "b": 63.8, "c_scale": 14.6, "modified": 1.0}, expected=(49.2, 63.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 64.2, "b": 80.8, "c_scale": 16.6, "modified": 1.0}, expected=(64.2, 80.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 81.2, "b": 99.8, "c_scale": 18.6, "modified": 1.0}, expected=(81.2, 99.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 100.2, "b": 120.8, "c_scale": 20.6, "modified": 1.0}, expected=(100.2, 120.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 121.2, "b": 143.8, "c_scale": 22.6, "modified": 1.0}, expected=(121.2, 143.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 144.3, "b": 168.7, "c_scale": 24.4, "modified": 1.0}, expected=(144.3, 168.7)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 169.3, "b": 195.7, "c_scale": 26.4, "modified": 1.0}, expected=(169.3, 195.7)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 196.3, "b": 224.7, "c_scale": 28.4, "modified": 1.0}, expected=(196.3, 224.7)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 225.3, "b": 255.7, "c_scale": 30.4, "modified": 1.0}, expected=(225.3, 255.7)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 256.3, "b": 288.7, "c_scale": 32.4, "modified": 1.0}, expected=(256.3, 288.7)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 289.4, "b": 323.6, "c_scale": 34.2, "modified": 1.0}, expected=(289.4, 323.6)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 324.4, "b": 360.6, "c_scale": 36.2, "modified": 1.0}, expected=(324.4, 360.6)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 361.4, "b": 399.6, "c_scale": 38.2, "modified": 1.0}, expected=(361.4, 399.6)
        ),
    )
