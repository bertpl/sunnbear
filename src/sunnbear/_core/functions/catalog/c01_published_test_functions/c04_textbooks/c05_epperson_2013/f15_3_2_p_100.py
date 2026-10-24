"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.2 (p. 100), Fig. 3.4, Table 3.3; Ex. 3.19, Table 3.16`` in the survey
of published test problems. The module generator, `scripts/literature_test_problems/formula_modules.py`, does not write
a formula with the parameter ``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson201332P100(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(20*x - 1)/(19*x)``; the formula's intervals are `[0.01, 1]` (Table
    3.16); `[-0.2, 0.2]` (Fig. 3.4).

    Root 0.05. Table 3.3: the first Newton step from `x0 = 1, 0.5, 0.25, 0.125, 0.0625` gives `x1 < 0` until `x0 =
    1/16`. Table 3.16: the hybrid method (Algorithm 3.6), from `x0 = 0.01, x1 = 1`.

    With ``modified = 1``, the interval ``[-0.2, 0.2]`` becomes ``[0.01, 0.2]``: its lower bound moves right of the pole
    at 0, to the lower bound of the formula's other published interval, so that the interval holds its root and no pole.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function on ``[-0.2, 0.2]`` fails a benchmark suite's checks of its test functions, because the
    pole at 0 is a second sign change, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 5, 15)
    name = "§3.2 (p. 100)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="§3.2 (p. 100), Fig. 3.4, Table 3.3; Ex. 3.19, Table 3.16",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (20 * x - 1) / (19 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.01, 1.0, 0.99, 0.0),
                    (-0.2, 0.2, 0.4, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.01, 0.2, 0.19, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 0.0}, x=0.307, c=0.0, expected=0.8811932110406309
        ),
        FormulaTestCase.value(
            params={"a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 0.0},
            x=0.307,
            c=0.25,
            expected=0.16806722689075626,
        ),
        FormulaTestCase.value(
            params={"a": -0.2, "b": 0.2, "c_scale": 0.4, "modified": 0.0}, x=-0.08, c=0.0, expected=1.7105263157894737
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 0.0}, expected=(0.01, 1.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.2, "b": 0.2, "c_scale": 0.4, "modified": 0.0}, expected=(-0.2, 0.2)
        ),
        FormulaTestCase.value(
            params={"a": 0.01, "b": 0.2, "c_scale": 0.19, "modified": 1.0},
            x=0.067,
            c=0.25,
            expected=-1.6464237516869091,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.01, "b": 0.2, "c_scale": 0.19, "modified": 1.0}, expected=(0.01, 0.2)
        ),
    )
