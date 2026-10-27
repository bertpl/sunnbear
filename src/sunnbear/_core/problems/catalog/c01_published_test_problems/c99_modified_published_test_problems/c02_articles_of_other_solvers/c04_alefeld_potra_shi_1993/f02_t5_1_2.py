"""This module holds formula f1.99.2.4.2, the modified version of the published formula f1.2.4.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.4.2 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedAlefeldPotraShi1993T512(Formula):
    """This formula is the modified version of formula f1.2.4.2, from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``-2*sum((2*i - 5)^2/(x - i^2)^3, i = 1..20)``, with the parameters ``n =
    1(1)19``; the published intervals are `[a_n, b_n]` with `a_n = n^2 + 10^(-9)`, `b_n = (n + 1)^2 - 10^(-9)`.

    `n` only selects the interval between the poles at `n^2` and `(n + 1)^2`; `f` has no parameter.

    The formula moves each bound away from its pole, at ``n^2`` or ``(n + 1)^2``, to a distance of 1% of the published
    interval's width, rounded half up to 1 significant digit, such as ``[1.03, 3.97]`` for ``n = 1``.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because each bound lies
    ``1e-9`` from a pole, so that a shift along x by more than ``1e-9`` crosses it.

    The modification changes what the test problem tests: at the published bounds, ``abs(f)`` is at least about 2e27,
    and at the modified bounds ``abs(f)`` is at most about 7e5, so the modified intervals leave out the steepest part of
    f next to each pole.
    """

    number = (1, 99, 2, 4, 2)
    name = "T5.1-2"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear "
            "equations. Mathematics of Computation 61(204), 733–744. "
            "https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        location="T5.1-2",
    )

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
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (1.03, 3.97, 2.94),
                    (4.05, 8.95, 4.9),
                    (9.07, 15.93, 6.86),
                    (16.09, 24.91, 8.82),
                    (25.1, 35.9, 10.8),
                    (36.1, 48.9, 12.8),
                    (49.2, 63.8, 14.6),
                    (64.2, 80.8, 16.6),
                    (81.2, 99.8, 18.6),
                    (100.2, 120.8, 20.6),
                    (121.2, 143.8, 22.6),
                    (144.3, 168.7, 24.4),
                    (169.3, 195.7, 26.4),
                    (196.3, 224.7, 28.4),
                    (225.3, 255.7, 30.4),
                    (256.3, 288.7, 32.4),
                    (289.4, 323.6, 34.2),
                    (324.4, 360.6, 36.2),
                    (361.4, 399.6, 38.2),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.03, "b": 3.97, "c_scale": 2.94}, x=1.912, c=0.25, expected=-3245.921784746983
        ),
        FormulaTestCase.value(
            params={"a": 4.05, "b": 8.95, "c_scale": 4.9}, x=5.52, c=0.25, expected=-78.36316187459528
        ),
        FormulaTestCase.value(
            params={"a": 9.07, "b": 15.93, "c_scale": 6.86}, x=11.128, c=0.25, expected=-28.3452146369843
        ),
        FormulaTestCase.value(
            params={"a": 16.09, "b": 24.91, "c_scale": 8.82}, x=18.736, c=0.25, expected=-120.12748402260388
        ),
        FormulaTestCase.value(
            params={"a": 25.1, "b": 35.9, "c_scale": 10.8}, x=28.34, c=0.25, expected=-190.6464124364607
        ),
        FormulaTestCase.value(
            params={"a": 36.1, "b": 48.9, "c_scale": 12.8}, x=39.94, c=0.25, expected=-241.7666581280263
        ),
        FormulaTestCase.value(
            params={"a": 49.2, "b": 63.8, "c_scale": 14.6}, x=53.58, c=0.25, expected=-201.33743333034084
        ),
        FormulaTestCase.value(
            params={"a": 64.2, "b": 80.8, "c_scale": 16.6}, x=69.18, c=0.25, expected=-221.40818669786006
        ),
        FormulaTestCase.value(
            params={"a": 81.2, "b": 99.8, "c_scale": 18.6}, x=86.78, c=0.25, expected=-234.2023727016661
        ),
        FormulaTestCase.value(
            params={"a": 100.2, "b": 120.8, "c_scale": 20.6}, x=106.38, c=0.25, expected=-241.78013013008834
        ),
        FormulaTestCase.value(
            params={"a": 121.2, "b": 143.8, "c_scale": 22.6}, x=127.98, c=0.25, expected=-245.6439159946042
        ),
        FormulaTestCase.value(
            params={"a": 144.3, "b": 168.7, "c_scale": 24.4}, x=151.62, c=0.25, expected=-205.55688252354955
        ),
        FormulaTestCase.value(
            params={"a": 169.3, "b": 195.7, "c_scale": 26.4}, x=177.22, c=0.25, expected=-207.42303764882604
        ),
        FormulaTestCase.value(
            params={"a": 196.3, "b": 224.7, "c_scale": 28.4}, x=204.82, c=0.25, expected=-207.89309828829218
        ),
        FormulaTestCase.value(
            params={"a": 225.3, "b": 255.7, "c_scale": 30.4}, x=234.42, c=0.25, expected=-207.31984414032246
        ),
        FormulaTestCase.value(
            params={"a": 256.3, "b": 288.7, "c_scale": 32.4}, x=266.02, c=0.25, expected=-205.9698269587908
        ),
        FormulaTestCase.value(
            params={"a": 289.4, "b": 323.6, "c_scale": 34.2}, x=299.66, c=0.25, expected=-179.0296896097693
        ),
        FormulaTestCase.value(
            params={"a": 324.4, "b": 360.6, "c_scale": 36.2}, x=335.26, c=0.25, expected=-178.04540523008717
        ),
        FormulaTestCase.value(
            params={"a": 361.4, "b": 399.6, "c_scale": 38.2}, x=372.86, c=0.25, expected=-176.68235557293022
        ),
        FormulaTestCase.interval_bounds(params={"a": 1.03, "b": 3.97, "c_scale": 2.94}, expected=(1.03, 3.97)),
        FormulaTestCase.interval_bounds(params={"a": 4.05, "b": 8.95, "c_scale": 4.9}, expected=(4.05, 8.95)),
        FormulaTestCase.interval_bounds(params={"a": 9.07, "b": 15.93, "c_scale": 6.86}, expected=(9.07, 15.93)),
        FormulaTestCase.interval_bounds(params={"a": 16.09, "b": 24.91, "c_scale": 8.82}, expected=(16.09, 24.91)),
        FormulaTestCase.interval_bounds(params={"a": 25.1, "b": 35.9, "c_scale": 10.8}, expected=(25.1, 35.9)),
        FormulaTestCase.interval_bounds(params={"a": 36.1, "b": 48.9, "c_scale": 12.8}, expected=(36.1, 48.9)),
        FormulaTestCase.interval_bounds(params={"a": 49.2, "b": 63.8, "c_scale": 14.6}, expected=(49.2, 63.8)),
        FormulaTestCase.interval_bounds(params={"a": 64.2, "b": 80.8, "c_scale": 16.6}, expected=(64.2, 80.8)),
        FormulaTestCase.interval_bounds(params={"a": 81.2, "b": 99.8, "c_scale": 18.6}, expected=(81.2, 99.8)),
        FormulaTestCase.interval_bounds(params={"a": 100.2, "b": 120.8, "c_scale": 20.6}, expected=(100.2, 120.8)),
        FormulaTestCase.interval_bounds(params={"a": 121.2, "b": 143.8, "c_scale": 22.6}, expected=(121.2, 143.8)),
        FormulaTestCase.interval_bounds(params={"a": 144.3, "b": 168.7, "c_scale": 24.4}, expected=(144.3, 168.7)),
        FormulaTestCase.interval_bounds(params={"a": 169.3, "b": 195.7, "c_scale": 26.4}, expected=(169.3, 195.7)),
        FormulaTestCase.interval_bounds(params={"a": 196.3, "b": 224.7, "c_scale": 28.4}, expected=(196.3, 224.7)),
        FormulaTestCase.interval_bounds(params={"a": 225.3, "b": 255.7, "c_scale": 30.4}, expected=(225.3, 255.7)),
        FormulaTestCase.interval_bounds(params={"a": 256.3, "b": 288.7, "c_scale": 32.4}, expected=(256.3, 288.7)),
        FormulaTestCase.interval_bounds(params={"a": 289.4, "b": 323.6, "c_scale": 34.2}, expected=(289.4, 323.6)),
        FormulaTestCase.interval_bounds(params={"a": 324.4, "b": 360.6, "c_scale": 36.2}, expected=(324.4, 360.6)),
        FormulaTestCase.interval_bounds(params={"a": 361.4, "b": 399.6, "c_scale": 38.2}, expected=(361.4, 399.6)),
    )
