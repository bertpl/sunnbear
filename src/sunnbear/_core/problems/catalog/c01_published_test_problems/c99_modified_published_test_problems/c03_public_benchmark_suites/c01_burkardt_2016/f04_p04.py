"""This module holds formula f1.99.3.1.4, the modified version of the published formula f1.3.1.4.

A change of formula f1.3.1.4 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurkardt2016P04(Formula):
    """This formula is the modified version of formula f1.3.1.4, from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 1.0/(100.0*x*x)``; the published intervals are `[0.00001,
    20.0]` (rang); `[0.03, 1.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.03` and `1.0`.

    The formula holds only the test problem on ``[1e-05, 20]``. The formula evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on that interval, ``[a, b]``: ``c`` scales x, so that the root moves by the factor
    ``(b/a)**c`` and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problem on ``[1e-05, 20]`` does not satisfy the benchmark suite inclusion conditions, because
    the interval spans orders of magnitude next to the pole of ``1/(100*x*x)`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 99, 3, 1, 4)
    name = "p04"
    params = ()
    location_in_publication = "Problem p04"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x e^{-\c \ln(20/10^{-5})}"),),
        expression=r"e^{\tmp{u}} - \frac{1.0}{100.0 \tmp{u} \tmp{u}}",
        interval="[10^{-5}, 20]",
        notes=(
            (
                r"$\c$ scales x, so that the root moves by the factor $(20/10^{-5})^{\c}$ and never "
                "reaches 0: the interval spans orders of magnitude next to the pole at 0, and a shift "
                "along x would move the lower bound across it."
            ),
        ),
    )
    effect_of_c = EffectOfC.SCALES_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``, with ``[a, b] = [1e-05, 20]``."""
        x = x * math.exp(-c * math.log(20.0 / 1e-05))
        return math.exp(x) - 1.0 / (100.0 * x * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1e-05, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (FormulaTestCase.value(params={}, x=0.0603418, c=0.25, expected=-3882.9917266298216),)
