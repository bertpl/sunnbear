"""This module holds what the power function formulas share: the axes of their recipes, and the rule for ``[d, 1]``.

Every formula of the category sweeps its power ``p`` on a logarithmic scale with the same step (`power_axis`).

`NearEdgePower` and `NearPolePower` share the interval ``[d, 1]``, the distances ``d`` that they sweep
(`distance_axis`), and the rule for a pair of ``p`` and ``d`` whose function has a root in that interval
(`has_root_inside_interval`).
"""

from sunnbear._core.problems.core import ParamAxis, ParamNotation

# Each recipe of the category sweeps the exponent of ``p = 10^exponent`` in steps of this size.
POWER_EXPONENT_STEP = 0.1


def power_axis(lowest_exponent: float, highest_exponent: float) -> ParamAxis:
    """Return the axis of the powers ``p`` from ``10^lowest_exponent`` to ``10^highest_exponent``.

    The exponent runs in steps of `POWER_EXPONENT_STEP`.
    """
    return ParamAxis("p", lowest_exponent, highest_exponent, POWER_EXPONENT_STEP, ParamNotation.POW10)


def distance_axis() -> ParamAxis:
    """Return the axis of the distances ``d`` from 10^-6 to 10^-1, with the exponent in steps of 1."""
    return ParamAxis("d", -6.0, -1.0, 1.0, ParamNotation.POW10)


def has_root_inside_interval(p: float, d: float) -> bool:
    """Return whether ``d^p < 0.5``, which gives the function a root inside ``[d, 1]`` at ``c = 0``.

    `NearEdgePower` is ``x^p - 0.5 + c`` and `NearPolePower` is ``(d/x)^p - 0.5 + c``. At ``c = 0``, each has the value
    0.5 at 1 bound of ``[d, 1]`` and ``d^p - 0.5`` at the other, so its values at the bounds have opposite signs only
    when ``d^p < 0.5``.
    """
    return d**p < 0.5
