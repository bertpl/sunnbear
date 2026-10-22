"""This module holds the formula of 4 in Alefeld, Potra, Shi (1995).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1995_alefeld_potra_shi`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "b95999341bd2b1cd"


class AlefeldPotraShi19954(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x^n - a``, with the parameters ``on `[0, 5]`: `a = 0.2, 1`, `n = 4(2)12`; on `[-0.95, 4.05]`: `a
    = 1`, `n = 8(2)14```; the formula's interval is `[0, 5]`; `[-0.95, 4.05]`.

    Driver problems 15 (`a = 0.2` on `[0, 5]`), 16 (`a = 1` on `[0, 5]`) and 17 (`a = 1` on `[-0.95, 4.05]`).
    """

    number = (1, 1, 6, 1)
    name = "4"
    param_names = ("a_", "n", "a", "b")
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344. "
            "https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748: "
            "https://www.netlib.org/toms/748."
        ),
        location="4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, n: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return x**n - a_

    def interval_bounds(self, a_: float, n: float, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "n", "a", "b"),
                rows=(
                    (
                        0.2,
                        4.0,
                        0.0,
                        5.0,
                    ),
                    (
                        0.2,
                        6.0,
                        0.0,
                        5.0,
                    ),
                    (
                        0.2,
                        8.0,
                        0.0,
                        5.0,
                    ),
                    (
                        0.2,
                        10.0,
                        0.0,
                        5.0,
                    ),
                    (
                        0.2,
                        12.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        4.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        6.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        8.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        10.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        12.0,
                        0.0,
                        5.0,
                    ),
                    (
                        1.0,
                        8.0,
                        -0.95,
                        4.05,
                    ),
                    (
                        1.0,
                        10.0,
                        -0.95,
                        4.05,
                    ),
                    (
                        1.0,
                        12.0,
                        -0.95,
                        4.05,
                    ),
                    (
                        1.0,
                        14.0,
                        -0.95,
                        4.05,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=4.8625),
        FormulaTestCase.value(params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.25, expected=-0.19609375),
        FormulaTestCase.value(params={"a_": 0.2, "n": 6.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=11.190625),
        FormulaTestCase.value(params={"a_": 0.2, "n": 8.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=25.42890625),
        FormulaTestCase.value(params={"a_": 0.2, "n": 10.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=57.4650390625),
        FormulaTestCase.value(
            params={"a_": 0.2, "n": 12.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=129.546337890625
        ),
        FormulaTestCase.value(params={"a_": 1.0, "n": 4.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=4.0625),
        FormulaTestCase.value(params={"a_": 1.0, "n": 6.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=10.390625),
        FormulaTestCase.value(params={"a_": 1.0, "n": 8.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=24.62890625),
        FormulaTestCase.value(params={"a_": 1.0, "n": 10.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=56.6650390625),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 12.0, "a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=128.746337890625
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 8.0, "a": -0.95, "b": 4.05}, x=0.55, c=0.0, expected=-0.9916266062109375
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 10.0, "a": -0.95, "b": 4.05}, x=0.55, c=0.0, expected=-0.9974670483788086
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 12.0, "a": -0.95, "b": 4.05}, x=0.55, c=0.0, expected=-0.9992337821345896
        ),
        FormulaTestCase.value(
            params={"a_": 1.0, "n": 14.0, "a": -0.95, "b": 4.05}, x=0.55, c=0.0, expected=-0.9997682190957133
        ),
        FormulaTestCase.interval_bounds(params={"a_": 0.2, "n": 4.0, "a": 0.0, "b": 5.0}, expected=(0.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a_": 1.0, "n": 8.0, "a": -0.95, "b": 4.05}, expected=(-0.95, 4.05)),
    )
