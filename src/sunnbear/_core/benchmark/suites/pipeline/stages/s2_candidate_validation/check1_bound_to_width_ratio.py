"""The bound-to-width ratio check rejects a candidate whose interval lies far from 0 relative to its width.

A candidate is rejected when its bound-to-width ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds
`MAX_BOUND_TO_WIDTH_RATIO`.

Rounding a bound to float64, as bisection does when a midpoint becomes a new bound, changes the interval's width by up
to about ``eps * max(abs(a), abs(b))``, with ``eps`` the float64 machine epsilon; relative to the width, that change is
about ``eps`` times the bound-to-width ratio.

Bisection's evaluation count changes by 1 wherever ``(b - a) / (2*xtol)`` crosses a power of 2, so for an ``xtol`` at
which that quotient is close to a power of 2, the change in width can shift the count by 1.

`compute_xtol_range` keeps ``xtol`` away from those values by a margin that grows with the bound-to-width ratio, so a
larger ratio narrows the benchmark's sampled range of ``xtol`` values; the check keeps that margin small.

`MAX_BOUND_TO_WIDTH_RATIO` is stricter than the largest bound-to-width ratio that `compute_xtol_range` accepts for
users' own functions at the default `n_bisection_fevals`.
"""

import polars as pl

# A candidate whose bound-to-width ratio exceeds this limit is rejected by the bound-to-width ratio check.
MAX_BOUND_TO_WIDTH_RATIO = 100.0


def exceeds_max_bound_to_width_ratio() -> pl.Expr:
    """Return the expression that is true for each candidate whose bound-to-width ratio exceeds the limit.

    The expression reads the columns ``a`` and ``b``.
    """
    bound_to_width_ratio = pl.max_horizontal(pl.col("a").abs(), pl.col("b").abs()) / (pl.col("b") - pl.col("a"))
    return bound_to_width_ratio > MAX_BOUND_TO_WIDTH_RATIO
