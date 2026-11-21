"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``driver`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Norton1985Driver(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``x^7 + 28*x^4 - 480``; the formula's interval is ``[1, 2]``.

    From the code's `DRIVER`, not the article. Its sample output gives the zero `1.922884153250999`.
    """

    number = (1, 2, 2, 7)
    name = "driver"
    params = ()
    source = FormulaSource(
        reference=(
            "Norton, V. (1985). Algorithm 631: Finding a bracketed zero by Larkin's method of rational "
            "interpolation. ACM Transactions on Mathematical Software 11(2), 120–134. "
            "https://doi.org/10.1145/214392.214396. The author's Fortran code is Algorithm 631 of the "
            "Collected Algorithms of the ACM (CALGO), https://www.netlib.org/toms/631."
        ),
        location="the driver of the author's code",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{7} + 28 \tmp{u}^{4} - 480",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**7 + 28 * x**4 - 480

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-393.7543483),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-444.55872457734375),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
