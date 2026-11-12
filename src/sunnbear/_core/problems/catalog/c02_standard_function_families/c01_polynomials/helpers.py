"""This module holds what the polynomial formulas share: the validity rule of a power and the parameter recipes.

The formulas with a weight ``p`` share 1 recipe, and the formulas with a slope ``s`` share another, so that 2 formulas
with the same parameter sweep the same values of it.
"""

from sunnbear._core.problems.core import ParamAxis, ParamGrid, ParamNotation, ParamRecipe, ParamTable

# The recipes sweep the power ``n`` up to this value.
HIGHEST_POWER = 10

# No parameter notation spells a negative power of 10. The negative slopes are therefore the negatives of 10^-1 to
# 10^1 in steps of 10^0.1, each rounded to 3 significant digits, which the decimal notation spells.
_NEGATIVE_SLOPES = tuple(-float(f"{10.0 ** (tenths / 10):.3g}") for tenths in range(-10, 11))


def is_valid_power(n: float, lowest_power: int) -> bool:
    """Return whether `n` is an integer of at least `lowest_power` with the same parity as `lowest_power`."""
    if n != int(n):
        return False
    else:
        return n >= lowest_power and (int(n) - lowest_power) % 2 == 0


def power_and_weight_recipes(lowest_power: int) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula with the parameters ``n`` and ``p``.

    The recipes combine every power of `_power_axis` with every weight ``p`` from 10^-1 to 10^3 in steps of 10^0.1.
    Below 10^-1, the function is nearly the line ``x`` for every power.
    """
    weight_axis = ParamAxis("p", -1.0, 3.0, 0.1, ParamNotation.POW10)
    return (ParamGrid(axes=(_power_axis(lowest_power), weight_axis)),)


def power_and_slope_recipes(lowest_power: int) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula with the parameters ``n`` and ``s``.

    The recipes combine every power of `_power_axis` with 3 sets of slopes ``s``:

    - from 10^-2 to 10^-0.1 in steps of 10^0.1. Below 10^-2, the function differs from the one at ``s = 0`` only
      close to ``x = 0``, where few values of ``c`` put the root;
    - 0;
    - the negative slopes from -0.1 to -10 (`_NEGATIVE_SLOPES`).
    """
    power_axis = _power_axis(lowest_power)
    positive_slope_axis = ParamAxis("s", -2.0, -0.1, 0.1, ParamNotation.POW10)
    zero_slope_axis = ParamAxis("s", 0.0, 0.0, 1.0)
    negative_slope_rows = tuple((n, s) for n in power_axis.values() for s in _NEGATIVE_SLOPES)
    return (
        ParamGrid(axes=(power_axis, positive_slope_axis)),
        ParamGrid(axes=(power_axis, zero_slope_axis)),
        ParamTable(names=("n", "s"), rows=negative_slope_rows),
    )


def _power_axis(lowest_power: int) -> ParamAxis:
    """Return the axis of the powers ``n`` from `lowest_power` in steps of 2, up to `HIGHEST_POWER` at most."""
    highest_power = HIGHEST_POWER - (HIGHEST_POWER - lowest_power) % 2
    return ParamAxis("n", float(lowest_power), float(highest_power), 2.0)
