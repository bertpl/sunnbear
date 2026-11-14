"""This module holds what the polynomial formulas share: the validity rules of their parameters and their recipes.

All formulas with a weight ``w`` build their recipes with `weight_recipes`, so they sweep the same weights; all
formulas with a slope ``m`` build them with `slope_recipes`, so they sweep the same slopes.
"""

from sunnbear._core.problems.core import ParamAxis, ParamGrid, ParamNotation, ParamRecipe

# No recipe of the category uses a power above this value.
HIGHEST_POWER = 10


def is_valid_power(p: float, lowest_power: int) -> bool:
    """Return whether `p` is an integer of at least `lowest_power` with the same parity as `lowest_power`."""
    if p != int(p):
        return False
    else:
        return p >= lowest_power and (int(p) - lowest_power) % 2 == 0


def is_valid_term_count(n: float) -> bool:
    """Return whether `n` is an integer of at least 2, the smallest number of terms of a sum."""
    return n == int(n) and n >= 2


def power_axis(lowest_power: int) -> ParamAxis:
    """Return the axis of the powers ``p`` from `lowest_power` in steps of 2, up to `HIGHEST_POWER` at most."""
    highest_power = HIGHEST_POWER - (HIGHEST_POWER - lowest_power) % 2
    return ParamAxis("p", float(lowest_power), float(highest_power), 2.0)


def term_count_axis(lowest_power: int) -> ParamAxis:
    """Return the axis of the numbers of terms ``n`` of a sum of every 2nd power from `lowest_power`.

    The axis runs from 2 terms to the largest number of terms whose highest power is `HIGHEST_POWER` at most.
    """
    highest_term_count = (HIGHEST_POWER - lowest_power) // 2 + 1
    return ParamAxis("n", 2.0, float(highest_term_count), 1.0)


def weight_recipes(first_axis: ParamAxis) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula whose parameters are that of `first_axis` and a weight ``w``.

    The recipes combine every value of `first_axis` with every weight ``w`` from 10^-1 to 10^3, with the exponent in
    steps of 0.1. Below 10^-1, the function is nearly the line ``x``.
    """
    weight_axis = ParamAxis("w", -1.0, 3.0, 0.1, ParamNotation.POW10)
    return (ParamGrid(axes=(first_axis, weight_axis)),)


def slope_recipes(first_axis: ParamAxis) -> tuple[ParamRecipe, ...]:
    """Return the recipes of a formula whose parameters are that of `first_axis` and a slope ``m``.

    The recipes combine every value of `first_axis` with 3 sets of slopes ``m``:

    - from 10^-2 to 10^-0.1, with the exponent in steps of 0.1, stopping below 1 because at ``m = 1`` the function is
      the line ``x + c`` of `Linear`. Below 10^-2, the function differs from the one at ``m = 0`` only close to
      ``x = 0``, and few values of ``c`` place the root there;
    - 0;
    - from -10^-1 to -10^1, with the exponent in steps of 0.1.
    """
    positive_slope_axis = ParamAxis("m", -2.0, -0.1, 0.1, ParamNotation.POW10)
    zero_slope_axis = ParamAxis("m", 0.0, 0.0, 1.0)
    negative_slope_axis = ParamAxis("m", -1.0, 1.0, 0.1, ParamNotation.NEG_POW10)
    return (
        ParamGrid(axes=(first_axis, positive_slope_axis)),
        ParamGrid(axes=(first_axis, zero_slope_axis)),
        ParamGrid(axes=(first_axis, negative_slope_axis)),
    )
