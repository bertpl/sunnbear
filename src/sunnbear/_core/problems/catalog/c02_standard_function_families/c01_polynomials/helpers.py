"""This module holds what the polynomial formulas share: the validity rule of a power and the parameter recipes.

The formulas with a weight ``p`` build their recipes with 1 function, and the formulas with a slope ``s`` with another,
so that 2 formulas with the same parameter sweep the same values of it.
"""

from sunnbear._core.problems.core import ParamAxis, ParamGrid, ParamNotation, ParamRecipe, ParamTable

# The recipes sweep the power ``n`` up to this value.
HIGHEST_N = 10

# No parameter notation spells a value of the form ``-10^k``. The negative slopes are therefore the negatives of 10^-1
# to 10^1 in steps of 10^0.1, each rounded to 3 significant digits, which the decimal notation spells.
_NEGATIVE_SLOPES = tuple(-float(f"{10.0 ** (tenths / 10):.3g}") for tenths in range(-10, 11))


def is_valid_power(n: float, lowest_n: int) -> bool:
    """Return whether `n` is an integer of at least `lowest_n` with the same parity as `lowest_n`."""
    if n != int(n):
        return False
    else:
        return n >= lowest_n and (int(n) - lowest_n) % 2 == 0


def power_and_weight_recipes(lowest_n: int) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula with the parameters ``n`` and ``p``.

    The recipes combine every power ``n`` from `lowest_n` in steps of 2, up to `HIGHEST_N` at most, with every weight
    ``p`` from 10^-1 to 10^3 in steps of 10^0.1. Below 10^-1, the function is nearly the line ``x`` for every power.
    """
    weight_axis = ParamAxis("p", -1.0, 3.0, 0.1, ParamNotation.POW10)
    return (ParamGrid(axes=(_power_axis(lowest_n), weight_axis)),)


def power_and_slope_recipes(lowest_n: int) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula with the parameters ``n`` and ``s``.

    The recipes combine every power ``n`` from `lowest_n` in steps of 2, up to `HIGHEST_N` at most, with 3 sets of
    slopes ``s``:

    - from 10^-2 to 10^-0.1 in steps of 10^0.1, stopping below 1 because at ``s = 1`` the function is the line
      ``x + c`` of `Linear` for every ``n``. Below 10^-2, the function differs from the one at ``s = 0`` only close to
      ``x = 0``, and few values of ``c`` place the root there;
    - 0;
    - the negative slopes from -0.1 to -10 (`_NEGATIVE_SLOPES`).
    """
    power_axis = _power_axis(lowest_n)
    positive_slope_axis = ParamAxis("s", -2.0, -0.1, 0.1, ParamNotation.POW10)
    zero_slope_axis = ParamAxis("s", 0.0, 0.0, 1.0)
    negative_slope_rows = tuple((n, s) for n in power_axis.values() for s in _NEGATIVE_SLOPES)
    return (
        ParamGrid(axes=(power_axis, positive_slope_axis)),
        ParamGrid(axes=(power_axis, zero_slope_axis)),
        ParamTable(names=("n", "s"), rows=negative_slope_rows),
    )


def _power_axis(lowest_n: int) -> ParamAxis:
    """Return the axis of the powers ``n`` from `lowest_n` in steps of 2, up to `HIGHEST_N` at most."""
    highest_n = HIGHEST_N - (HIGHEST_N - lowest_n) % 2
    return ParamAxis("n", float(lowest_n), float(highest_n), 2.0)
