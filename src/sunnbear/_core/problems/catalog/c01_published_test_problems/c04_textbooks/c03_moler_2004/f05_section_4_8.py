"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7, §4.8; Ex. 4.7, 4.10(a)`` in the survey of published test problems.
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
from sunnbear._core.utils.math_functions import bessel_j0


class Moler2004Section48(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``J0(x)``; the formula's intervals are `[(n - 1)*pi, n*pi]`, `n = 1, ...,
    10` (§4.7); `[0, pi]` (§4.7, Ex. 4.7); `[0, 3.83]` (§4.8); `[0, 10*pi]` (Figure 4.2).

    The values ``pi``, ``2*pi``, ``3*pi``, ``4*pi``, ``5*pi``, ``6*pi``, ``7*pi``, ``8*pi``, ``9*pi``, ``10*pi`` are
    rounded to 12 significant digits, the most that a parameter value holds.

    §4.7 finds its first 10 zeros with `fzerotx`, 1 per interval, and plots it on `[0, 10*pi]` (Figure 4.2); it also
    calls `fzerotx(@bessj0,[0,pi])`. §4.8 steps `fzerogui` toward its first zero on `[0, 3.83]`, 3.83 being near its
    first local minimum (Figures 4.3–4.6). Ex. 4.7 calls `fzerotx(@besselj,[0 pi],0)`, which by `fzerotx`'s rule for
    extra arguments evaluates `besselj(x, 0)`, the Bessel function of order `x` at 0, and returns 3.1416; the exercise
    asks why. Ex. 4.10(a) asks for its first 10 zeros.
    """

    number = (1, 4, 3, 5)
    name = "Section 4.8"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§4.7, §4.8; Exercises 4.7, 4.10(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"J_{0}\left(\tmp{u}\right)",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"The Bessel function $J_0$, an oscillation of decaying amplitude, with 10 simple roots on $[0, 10\pi]$ and"
            r" 1 on each of the other intervals."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return bessel_j0(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (0.0, 3.14159265359, 3.14),
                    (3.14159265359, 6.28318530718, 3.14),
                    (6.28318530718, 9.42477796077, 3.14),
                    (9.42477796077, 12.5663706144, 3.14),
                    (12.5663706144, 15.7079632679, 3.14),
                    (15.7079632679, 18.8495559215, 3.14),
                    (18.8495559215, 21.9911485751, 3.14),
                    (21.9911485751, 25.1327412287, 3.14),
                    (25.1327412287, 28.2743338823, 3.14),
                    (28.2743338823, 31.4159265359, 3.14),
                    (0.0, 3.83, 3.83),
                    (0.0, 31.4159265359, 31.4),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, x=0.942478, c=0.0, expected=0.7899621483111053
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, x=0.942478, c=0.25, expected=0.9938097727352687
        ),
        FormulaTestCase.value(
            params={"a": 3.14159265359, "b": 6.28318530718, "c_scale": 3.14},
            x=4.08407,
            c=0.0,
            expected=-0.3902685790381638,
        ),
        FormulaTestCase.value(
            params={"a": 6.28318530718, "b": 9.42477796077, "c_scale": 3.14},
            x=7.22566,
            c=0.0,
            expected=0.29358225861332415,
        ),
        FormulaTestCase.value(
            params={"a": 9.42477796077, "b": 12.5663706144, "c_scale": 3.14},
            x=10.3673,
            c=0.0,
            expected=-0.24505800142850823,
        ),
        FormulaTestCase.value(
            params={"a": 12.5663706144, "b": 15.7079632679, "c_scale": 3.14},
            x=13.5088,
            c=0.0,
            expected=0.21464612299488564,
        ),
        FormulaTestCase.value(
            params={"a": 15.7079632679, "b": 18.8495559215, "c_scale": 3.14},
            x=16.6504,
            c=0.0,
            expected=-0.19331072218918294,
        ),
        FormulaTestCase.value(
            params={"a": 18.8495559215, "b": 21.9911485751, "c_scale": 3.14},
            x=19.792,
            c=0.0,
            expected=0.1772855618404285,
        ),
        FormulaTestCase.value(
            params={"a": 21.9911485751, "b": 25.1327412287, "c_scale": 3.14},
            x=22.9336,
            c=0.0,
            expected=-0.1646804794493179,
        ),
        FormulaTestCase.value(
            params={"a": 25.1327412287, "b": 28.2743338823, "c_scale": 3.14},
            x=26.0752,
            c=0.0,
            expected=0.15443011495630202,
        ),
        FormulaTestCase.value(
            params={"a": 28.2743338823, "b": 31.4159265359, "c_scale": 3.14},
            x=29.2168,
            c=0.0,
            expected=-0.14588234995066635,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.83, "c_scale": 3.83}, x=1.149, c=0.0, expected=0.6962046677389843
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4}, x=9.42478, c=0.0, expected=-0.1812118138919495
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, expected=(0.0, 3.14159265359)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 3.14159265359, "b": 6.28318530718, "c_scale": 3.14}, expected=(3.14159265359, 6.28318530718)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 6.28318530718, "b": 9.42477796077, "c_scale": 3.14}, expected=(6.28318530718, 9.42477796077)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 9.42477796077, "b": 12.5663706144, "c_scale": 3.14}, expected=(9.42477796077, 12.5663706144)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 12.5663706144, "b": 15.7079632679, "c_scale": 3.14}, expected=(12.5663706144, 15.7079632679)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 15.7079632679, "b": 18.8495559215, "c_scale": 3.14}, expected=(15.7079632679, 18.8495559215)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 18.8495559215, "b": 21.9911485751, "c_scale": 3.14}, expected=(18.8495559215, 21.9911485751)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 21.9911485751, "b": 25.1327412287, "c_scale": 3.14}, expected=(21.9911485751, 25.1327412287)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 25.1327412287, "b": 28.2743338823, "c_scale": 3.14}, expected=(25.1327412287, 28.2743338823)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 28.2743338823, "b": 31.4159265359, "c_scale": 3.14}, expected=(28.2743338823, 31.4159265359)
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 3.83, "c_scale": 3.83}, expected=(0.0, 3.83)),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4}, expected=(0.0, 31.4159265359)
        ),
    )
