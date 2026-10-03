"""The polars expressions `owg_expression` and `gpq_expression` give the results of `owg` and `gpq` per group."""

import numpy as np
import polars as pl
import pytest

from sunnbear._core.stats.pseudo_quantile_expressions import gpq_expression, owg_expression
from sunnbear.stats import gpq, owg

# The group with a zero is large enough that its smallest rank weight rounds to 0.0 in float64 at the `owg` power
# that `gpq` uses for level 0.99, which `owg_expression` handles as a separate case.
_RNG = np.random.default_rng(3)
_VALUES_BY_GROUP = {
    "lognormal": _RNG.lognormal(3.0, 1.0, 500),
    "counts": _RNG.integers(2, 60, 300).astype(float),
    "single": np.array([7.0]),
    "with_a_zero": np.linspace(0.0, 9.0, 1024),
}


def _frame() -> pl.DataFrame:
    """Return a frame with 1 row per value, and the group of each value in the column `group`."""
    return pl.DataFrame(
        {
            "group": [group for group, values in _VALUES_BY_GROUP.items() for _ in values],
            "value": np.concatenate(list(_VALUES_BY_GROUP.values())),
        }
    )


@pytest.mark.parametrize("q", [0.0, 0.1, 0.25, 0.5, 0.75, 0.99, 1.0])
def test_gpq_expression_equals_gpq_per_group(q):
    """Per group, the expression gives the value of `gpq`, at the endpoint levels and with a zero too."""
    # --- act --------------------------
    results = _frame().group_by("group").agg(gpq_expression("value", q).alias("gpq"))

    # --- assert -----------------------
    for group, result in results.iter_rows():
        assert result == pytest.approx(gpq(_VALUES_BY_GROUP[group], q), rel=1e-12)


@pytest.mark.parametrize("p", [-np.inf, -3.0, 0.0, 1.5, np.inf])
def test_owg_expression_equals_owg_per_group(p):
    """Per group, the expression gives the value of `owg`, at infinite powers too."""
    # --- act --------------------------
    results = _frame().group_by("group").agg(owg_expression("value", p).alias("owg"))

    # --- assert -----------------------
    for group, result in results.iter_rows():
        assert result == pytest.approx(owg(_VALUES_BY_GROUP[group], p), rel=1e-12)


@pytest.mark.parametrize("q", [-0.5, 1.5, float("nan")])
def test_gpq_expression_refuses_out_of_range_q(q):
    """An out-of-range or NaN level raises `ValueError` when the expression is built."""
    # --- act / assert -----------------
    with pytest.raises(ValueError):
        gpq_expression("value", q)
