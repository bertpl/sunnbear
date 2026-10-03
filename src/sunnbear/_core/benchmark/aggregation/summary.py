"""`summarize_results` summarizes a results table per group: its success fractions, and statistics of chosen columns.

The statistics are `gpq` levels, the geometric pseudo-quantiles of `sunnbear.stats`. Grouping is the caller's
choice of columns, e.g. `solver_id` for 1 row per solver, or `solver_id` and `function_id` for 1 row per pair.

Each `gpq` is computed over all rows of a group at once, so a test function that has more rows in a group, for
example because it ran on more samples, weighs more in that group's `gpq`.
"""

from collections.abc import Mapping, Sequence
from typing import overload

import polars as pl

from sunnbear._core.stats.pseudo_quantile_expressions import gpq_expression
from sunnbear._core.utils.polars_frames import collect_if_eager

from .derived_results import DERIVED_RESULTS_SCHEMA
from .helpers import is_converged_expression

# These are the `gpq` levels of each summarized column when the caller names none: a best-case, a typical and a
# worst-case value; `gpq` at level 0.5 is the geometric mean.
DEFAULT_GPQ_LEVELS = (0.25, 0.5, 0.75)


def gpq_column_name(column: str, q: float) -> str:
    """Return the summary column name for the `gpq` of `column` at level `q`, e.g. `n_fevals_eff_gpq_25`.

    The level is written in percent, with at least 2 digits: `gpq_05`, `gpq_50`, `gpq_100`, `gpq_12.5`.
    """
    return f"{column}_gpq_{f'{round(q * 100, 6):g}'.zfill(2)}"


@overload
def summarize_results(
    frame: pl.DataFrame,
    by: str | Sequence[str],
    *,
    gpq_levels_by_column: Mapping[str, Sequence[float]] | None = None,
) -> pl.DataFrame: ...
@overload
def summarize_results(
    frame: pl.LazyFrame,
    by: str | Sequence[str],
    *,
    gpq_levels_by_column: Mapping[str, Sequence[float]] | None = None,
) -> pl.LazyFrame: ...
def summarize_results(
    frame: pl.DataFrame | pl.LazyFrame,
    by: str | Sequence[str],
    *,
    gpq_levels_by_column: Mapping[str, Sequence[float]] | None = None,
) -> pl.DataFrame | pl.LazyFrame:
    """Return 1 row per group of `frame`, grouped by the columns `by`, in order of first appearance.

    Each row holds the group's values of `by`, and:

    - `converged_fraction`: the fraction of the group's solves that converged;
    - `correct_fraction`: the fraction that converged to a correct answer, so never more than
      `converged_fraction`;
    - for each summarized column and each of its levels `q`, the column's `gpq` at `q`, named by
      `gpq_column_name`.

    Each `gpq` is computed over all rows of a group at once, so a test function with more rows in the group weighs
    more in that group's `gpq`.

    Args:
        frame: A results table with the columns of `RESULTS_SCHEMA` and, for the default
            `gpq_levels_by_column`, the columns of `DERIVED_RESULTS_SCHEMA` (see `add_derived_results`);
            eager or lazy, and the result is of the same kind.
        by: The column or columns to group by.
        gpq_levels_by_column: The `gpq` levels to compute, per column. Each column must hold non-negative
            values, and each level must lie between 0 and 1 inclusive, where 0 gives the minimum and 1 the
            maximum. ``None`` summarizes every column of `DERIVED_RESULTS_SCHEMA` at `DEFAULT_GPQ_LEVELS`. The
            cost of the summary grows with the number of columns times levels, so on a large table, ask only
            for the levels you need.

    Raises:
        ValueError: If a level is outside [0, 1], if 2 levels of a column give the same summary column name,
            or if `frame` lacks a column to group by or to summarize.
    """
    if gpq_levels_by_column is None:
        gpq_levels_by_column = dict.fromkeys(DERIVED_RESULTS_SCHEMA, DEFAULT_GPQ_LEVELS)
    group_columns = [by] if isinstance(by, str) else list(by)
    _validate_has_columns(frame, [*group_columns, "status", "is_correct", *gpq_levels_by_column])

    # --- gpq columns ----------------------------
    gpq_columns = {
        gpq_column_name(column, q): gpq_expression(column, q)
        for column, levels in gpq_levels_by_column.items()
        for q in levels
    }
    n_requested_gpq_levels = sum(len(levels) for levels in gpq_levels_by_column.values())
    if len(gpq_columns) < n_requested_gpq_levels:
        raise ValueError(
            f"gpq_levels_by_column gives a summary column name more than once: {dict(gpq_levels_by_column)}."
        )

    # --- aggregate per group --------------------
    result = (
        frame.lazy()
        .group_by(group_columns, maintain_order=True)
        .agg(
            is_converged_expression().mean().alias("converged_fraction"),
            pl.col("is_correct").mean().alias("correct_fraction"),
            *(expression.alias(name) for name, expression in gpq_columns.items()),
        )
    )
    return collect_if_eager(frame, result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _validate_has_columns(frame: pl.DataFrame | pl.LazyFrame, columns: Sequence[str]) -> None:
    """Check that `frame` has every one of `columns`.

    Raises:
        ValueError: If a column is missing; the message points to `add_derived_results` for a derived column.
    """
    column_names = set(frame.collect_schema().names())
    missing_columns = [column for column in columns if column not in column_names]
    if missing_columns:
        raise ValueError(
            f"The results table lacks the columns {missing_columns}; "
            f"add the columns of DERIVED_RESULTS_SCHEMA with add_derived_results first."
            if set(missing_columns) & set(DERIVED_RESULTS_SCHEMA)
            else f"The results table lacks the columns {missing_columns}."
        )
