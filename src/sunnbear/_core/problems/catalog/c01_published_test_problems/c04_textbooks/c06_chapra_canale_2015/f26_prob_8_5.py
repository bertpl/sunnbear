"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 8.5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ChapraCanale2015Prob85(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``K = (cc0 + x)/((ca0 - 2*x)^2*(cb0 - x))``, with the parameters `K =
    0.015`, `ca0 = 42`, `cb0 = 30`, `cc0 = 4`; the formula's interval is ``[0, 20]``.

    Unknown `x`, the moles of C produced by the reversible reaction `2A + B = C`; `ca0`, `cb0` and `cc0` are the initial
    concentrations. Graphically, then by bisection or false position to `es = 0.5%`.
    """

    number = (1, 4, 6, 26)
    name = "Prob. 8.5"
    params = (
        FormulaParam("K", latex_symbol="K"),
        FormulaParam("ca0", latex_symbol="c_{a0}"),
        FormulaParam("cb0", latex_symbol="c_{b0}"),
        FormulaParam("cc0", latex_symbol="c_{c0}"),
    )
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 8.5",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\param{K} - \frac{\param{cc0} + \tmp{u}}{\left(\param{ca0} - 2 \tmp{u}\right)^{2} "
            r"\left(\param{cb0} - \tmp{u}\right)}"
        ),
        interval="[0, 20]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, K: float, ca0: float, cb0: float, cc0: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return (K) - ((cc0 + x) / ((ca0 - 2 * x) ** 2 * (cb0 - x)))

    def interval_bounds(self, K: float, ca0: float, cb0: float, cc0: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("K", "ca0", "cb0", "cc0"),
                rows=((0.015, 42.0, 30.0, 4.0),),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"K": 0.015, "ca0": 42.0, "cb0": 30.0, "cc0": 4.0}, x=6.0, c=0.0, expected=0.014537037037037038
        ),
        FormulaTestCase.value(
            params={"K": 0.015, "ca0": 42.0, "cb0": 30.0, "cc0": 4.0}, x=6.0, c=0.25, expected=0.014892241379310344
        ),
        FormulaTestCase.interval_bounds(
            params={"K": 0.015, "ca0": 42.0, "cb0": 30.0, "cc0": 4.0}, expected=(0.0, 20.0)
        ),
    )
