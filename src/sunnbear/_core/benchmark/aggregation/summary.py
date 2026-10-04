"""`summarize_results` gives each group's converged and correct fractions and geometric pseudo-quantiles (`gpq`)."""

from collections.abc import Mapping, Sequence
from typing import overload

import polars as pl

from sunnbear._core.solvers.core import SolveStatus
from sunnbear._core.stats.pseudo_quantile_expressions import gpq_expression

from .derived_results import DERIVED_RESULTS_SCHEMA

# These are the `gpq` levels of each summarized column when the caller names none: a low, a typical and a high
# value; `gpq` at level 0.5 is the geometric mean.
DEFAULT_GPQ_LEVELS = (0.25, 0.5, 0.75)


def gpq_column_name(column: str, q: float) -> str:
    """Return the summary column name for the `gpq` of `column` at level `q`, e.g. `n_fevals_eff_gpq_25`.

    The level is written in percent, with at least 2 digits: `gpq_05`, `gpq_50`, `gpq_100`, `gpq_12.5`. The
    percentage keeps 6 significant digits, so 2 levels that agree to that precision get the same name.
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
    """Return 1 row per group of `frame`, grouped by the columns `by`, in the order in which the groups first appear.

    Each row holds the group's values of `by`, and:

    - `converged_fraction`: the fraction of the group's solves that converged;
    - `correct_fraction`: the fraction that converged to a correct answer, so never more than
      `converged_fraction`;
    - for each summarized column and each of its levels `q`, the column's `gpq` at `q`, named by
      `gpq_column_name`.

    Each `gpq` is computed over all rows of a group at once, so a test function (`function_id`) with more rows in the
    group weighs more in that group's `gpq`.

    Args:
        frame: A results table with the columns of `RESULTS_SCHEMA` and, for the default
            `gpq_levels_by_column`, the columns of `DERIVED_RESULTS_SCHEMA` (see `add_derived_results`);
            a `DataFrame` or a `LazyFrame`, and the result is of the same kind.
        by: The column or columns to group by, e.g. `solver_id` for 1 row per solver, or `["solver_id", "function_id"]`
            for 1 row per pair.
        gpq_levels_by_column: The `gpq` levels to compute, per column; ``None`` summarizes every column of
            `DERIVED_RESULTS_SCHEMA` at `DEFAULT_GPQ_LEVELS`.

            - Each column must hold non-negative values and no nulls; neither is checked, and a violation gives a
              NaN, null or wrong `gpq`.
            - Each level must lie between 0 and 1 inclusive, where 0 gives the minimum and 1 the maximum.
            - The run time of the summary grows with the number of columns times the number of levels, so on a
              large table, ask only for the levels you need.

    Raises:
        ValueError: If any of these holds:

            - a level is outside [0, 1];
            - a column has 2 levels that give the same summary column name;
            - `frame` lacks a column to group by or to summarize.
    """
    if gpq_levels_by_column is None:
        gpq_levels_by_column = dict.fromkeys(DERIVED_RESULTS_SCHEMA, DEFAULT_GPQ_LEVELS)
    group_columns = [by] if isinstance(by, str) else list(by)
    _validate_has_columns(frame, [*group_columns, "status", "is_correct", *gpq_levels_by_column])

    # --- gpq columns ----------------------------
    gpq_expressions_by_gpq_column_name = {
        gpq_column_name(column, q): gpq_expression(column, q)
        for column, levels in gpq_levels_by_column.items()
        for q in levels
    }
    n_requested_gpq_columns = sum(len(levels) for levels in gpq_levels_by_column.values())
    if len(gpq_expressions_by_gpq_column_name) < n_requested_gpq_columns:
        raise ValueError(
            f"gpq_levels_by_column gives a summary column name more than once: {dict(gpq_levels_by_column)}."
        )

    # --- aggregate per group --------------------
    summary = (
        frame.lazy()
        .group_by(group_columns, maintain_order=True)
        .agg(
            _converged_expression().mean().alias("converged_fraction"),
            pl.col("is_correct").mean().alias("correct_fraction"),
            *(expression.alias(name) for name, expression in gpq_expressions_by_gpq_column_name.items()),
        )
    )
    # The caller gets back the kind it passed in: a `DataFrame` is collected, a `LazyFrame` stays a plan.
    return summary.collect() if isinstance(frame, pl.DataFrame) else summary


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _converged_expression() -> pl.Expr:
    """Return an expression that is true for a solve that converged, whether its answer is correct or not."""
    return pl.col("status") == SolveStatus.CONVERGED.value


def _validate_has_columns(frame: pl.DataFrame | pl.LazyFrame, columns: Sequence[str]) -> None:
    """Check that `frame` has every one of `columns`.

    Raises:
        ValueError: If a column is missing; when a missing column is a derived column, the message says to call
            `add_derived_results` first.
    """
    frame_columns = set(frame.collect_schema().names())
    missing_columns = [column for column in columns if column not in frame_columns]
    if missing_columns:
        raise ValueError(
            f"The results table lacks the columns {missing_columns}; "
            f"add the columns of DERIVED_RESULTS_SCHEMA with add_derived_results first."
            if set(missing_columns) & set(DERIVED_RESULTS_SCHEMA)
            else f"The results table lacks the columns {missing_columns}."
        )
