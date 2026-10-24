"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7, §4.8; Ex. 4.7, 4.10(a)`` in the survey of published test problems.
The module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import bessel_j0


class Moler20044748(Formula):
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

    With ``modified = 1``, the interval ``[0, 10*pi]`` becomes ``[0, 30]``: its upper bound moves between the last 2
    roots, so that the interval holds 9 of the 10 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function on ``[0, 10*pi]`` does not satisfy the benchmark suite inclusion conditions, because the
    published interval holds 10 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 3, 5)
    name = "§4.7, §4.8"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§4.7, §4.8; Ex. 4.7, 4.10(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return bessel_j0(x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0, 3.14159265359, 3.14, 0.0),
                    (3.14159265359, 6.28318530718, 3.14, 0.0),
                    (6.28318530718, 9.42477796077, 3.14, 0.0),
                    (9.42477796077, 12.5663706144, 3.14, 0.0),
                    (12.5663706144, 15.7079632679, 3.14, 0.0),
                    (15.7079632679, 18.8495559215, 3.14, 0.0),
                    (18.8495559215, 21.9911485751, 3.14, 0.0),
                    (21.9911485751, 25.1327412287, 3.14, 0.0),
                    (25.1327412287, 28.2743338823, 3.14, 0.0),
                    (28.2743338823, 31.4159265359, 3.14, 0.0),
                    (0.0, 3.83, 3.83, 0.0),
                    (0.0, 31.4159265359, 31.4, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 30.0, 30.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0},
            x=0.942478,
            c=0.0,
            expected=0.7899621483111053,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0},
            x=0.942478,
            c=0.25,
            expected=0.9938097727352687,
        ),
        FormulaTestCase.value(
            params={"a": 3.14159265359, "b": 6.28318530718, "c_scale": 3.14, "modified": 0.0},
            x=4.08407,
            c=0.0,
            expected=-0.3902685790381638,
        ),
        FormulaTestCase.value(
            params={"a": 6.28318530718, "b": 9.42477796077, "c_scale": 3.14, "modified": 0.0},
            x=7.22566,
            c=0.0,
            expected=0.29358225861332415,
        ),
        FormulaTestCase.value(
            params={"a": 9.42477796077, "b": 12.5663706144, "c_scale": 3.14, "modified": 0.0},
            x=10.3673,
            c=0.0,
            expected=-0.24505800142850823,
        ),
        FormulaTestCase.value(
            params={"a": 12.5663706144, "b": 15.7079632679, "c_scale": 3.14, "modified": 0.0},
            x=13.5088,
            c=0.0,
            expected=0.21464612299488564,
        ),
        FormulaTestCase.value(
            params={"a": 15.7079632679, "b": 18.8495559215, "c_scale": 3.14, "modified": 0.0},
            x=16.6504,
            c=0.0,
            expected=-0.19331072218918294,
        ),
        FormulaTestCase.value(
            params={"a": 18.8495559215, "b": 21.9911485751, "c_scale": 3.14, "modified": 0.0},
            x=19.792,
            c=0.0,
            expected=0.1772855618404285,
        ),
        FormulaTestCase.value(
            params={"a": 21.9911485751, "b": 25.1327412287, "c_scale": 3.14, "modified": 0.0},
            x=22.9336,
            c=0.0,
            expected=-0.1646804794493179,
        ),
        FormulaTestCase.value(
            params={"a": 25.1327412287, "b": 28.2743338823, "c_scale": 3.14, "modified": 0.0},
            x=26.0752,
            c=0.0,
            expected=0.15443011495630202,
        ),
        FormulaTestCase.value(
            params={"a": 28.2743338823, "b": 31.4159265359, "c_scale": 3.14, "modified": 0.0},
            x=29.2168,
            c=0.0,
            expected=-0.14588234995066635,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.83, "c_scale": 3.83, "modified": 0.0}, x=1.149, c=0.0, expected=0.6962046677389843
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4, "modified": 0.0},
            x=9.42478,
            c=0.0,
            expected=-0.1812118138919495,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14, "modified": 0.0}, expected=(0.0, 3.14159265359)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 3.14159265359, "b": 6.28318530718, "c_scale": 3.14, "modified": 0.0},
            expected=(3.14159265359, 6.28318530718),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 6.28318530718, "b": 9.42477796077, "c_scale": 3.14, "modified": 0.0},
            expected=(6.28318530718, 9.42477796077),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 9.42477796077, "b": 12.5663706144, "c_scale": 3.14, "modified": 0.0},
            expected=(9.42477796077, 12.5663706144),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 12.5663706144, "b": 15.7079632679, "c_scale": 3.14, "modified": 0.0},
            expected=(12.5663706144, 15.7079632679),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 15.7079632679, "b": 18.8495559215, "c_scale": 3.14, "modified": 0.0},
            expected=(15.7079632679, 18.8495559215),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 18.8495559215, "b": 21.9911485751, "c_scale": 3.14, "modified": 0.0},
            expected=(18.8495559215, 21.9911485751),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 21.9911485751, "b": 25.1327412287, "c_scale": 3.14, "modified": 0.0},
            expected=(21.9911485751, 25.1327412287),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 25.1327412287, "b": 28.2743338823, "c_scale": 3.14, "modified": 0.0},
            expected=(25.1327412287, 28.2743338823),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 28.2743338823, "b": 31.4159265359, "c_scale": 3.14, "modified": 0.0},
            expected=(28.2743338823, 31.4159265359),
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 3.83, "c_scale": 3.83, "modified": 0.0}, expected=(0.0, 3.83)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 31.4159265359, "c_scale": 31.4, "modified": 0.0}, expected=(0.0, 31.4159265359)
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 30.0, "c_scale": 30.0, "modified": 1.0}, x=9.0, c=0.25, expected=0.5118276717359181
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 30.0, "c_scale": 30.0, "modified": 1.0}, expected=(0.0, 30.0)
        ),
    )
