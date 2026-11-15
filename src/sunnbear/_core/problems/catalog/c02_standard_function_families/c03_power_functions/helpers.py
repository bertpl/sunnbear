"""This module holds what the power function formulas share: the axes of their recipes.

Every formula of the category sweeps its power ``p`` on a logarithmic scale with the same step (`power_axis`).

`NearEdgePower` and `NearPolePower` share the interval ``[d, 1]`` and the distances ``d`` that they sweep
(`distance_axis`).
"""

from sunnbear._core.problems.core import ParamAxis, ParamNotation

# Each recipe of the category sweeps ``log10(p)`` in steps of this size.
LOG10_POWER_STEP = 0.1


def power_axis(lowest_log10_power: float, highest_log10_power: float) -> ParamAxis:
    """Return the axis of the powers ``p`` from ``10^lowest_log10_power`` to ``10^highest_log10_power``.

    ``log10(p)`` runs in steps of `LOG10_POWER_STEP`.
    """
    return ParamAxis("p", lowest_log10_power, highest_log10_power, LOG10_POWER_STEP, ParamNotation.POW10)


def distance_axis() -> ParamAxis:
    """Return the axis of the distances ``d`` from 10^-6 to 10^-1, with ``log10(d)`` in steps of 1."""
    return ParamAxis("d", -6.0, -1.0, 1.0, ParamNotation.POW10)
