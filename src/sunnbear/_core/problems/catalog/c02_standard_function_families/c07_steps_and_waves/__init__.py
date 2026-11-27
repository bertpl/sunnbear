"""This category holds steps and waves: functions with jumps, and smooth approximations of a step.

The steps and waves give behaviors absent from the other families:

- a sign change at a jump between 2 finite levels, where the function has no root;
- many jumps in 1 interval, alone or between roots on linear ramps;
- a smooth step whose steepness a parameter sets, up to a step in float64, with ripples, an overshoot or exactly
  constant plateaus beside it.

A formula with a level ``d`` subtracts ``d`` from its function: ``d`` sets where the root lies between the 2 plateaus
or, at a jump, the ratio of the 2 levels beside the jump.

Every formula shifts ``x`` by a multiple of ``c``:

- **`FloorFunction` and `Smoothstep` scale the shift by ``n`` or ``b``,** the parameter that sets the interval's
  width, so that their c-ranges barely depend on it.
- **The others shift ``x`` by ``c`` itself.** The interval of `HeavisideStep`, `SquareWaveFourierPartialSum`,
  `ButterworthFilterGain` and `ChebyshevFilterGain` does not grow with a parameter; `SawtoothWave` and `PulseWave` are
  periodic, so their c-ranges are set by the distance from a bound to the nearest sign change, which is less than 1
  period at every ``n``.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_heaviside_step,
    f02_floor_function,
    f03_sawtooth_wave,
    f04_pulse_wave,
    f05_fourier_partial_sum_of_the_square_wave,
    f06_butterworth_filter_gain,
    f07_chebyshev_filter_gain,
    f08_smoothstep,
)


class StepsAndWaves(FormulaCategory):
    """`StepsAndWaves` is the category of steps, waves with jumps, and smooth approximations of a step."""

    number = (2, 7)
    name = "Steps and waves"
    description = (
        "Functions with jumps, such as the Heaviside step, the floor function and the sawtooth and pulse waves, and "
        "smooth approximations of a step: the square wave's Fourier partial sums, the gains of the Butterworth and "
        "Chebyshev filters, and the smoothstep. At a jump, the function changes sign without a root; a smooth step "
        "can be steeper than float64 resolves, with ripples, an overshoot or exactly constant plateaus beside it."
    )
