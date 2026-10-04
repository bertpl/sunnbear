"""Geometric pseudo-quantiles: smooth, log-space stand-ins for hard quantiles.

- `owg` (`ordered_weighted_geomean`), the ordered weighted geometric mean, weights sorted samples by a power law of
  their rank, so that the statistic ranges continuously from the minimum through the geometric mean to the maximum
  as its power varies;
- `gpq` (`geometric_pseudo_quantile`), the geometric pseudo-quantile, calibrates that power so that the weight
  distribution's center of mass sits at a requested quantile level.

Each module holds the numpy function and a polars expression that computes the same statistic per group of a frame.
"""

from .geometric_pseudo_quantile import gpq, gpq_expression, gpq_power_for_level
from .ordered_weighted_geomean import owg, owg_expression
