"""`summarize_results` gives 1 row per group, with the group's fractions of converged and of correct solves and the
`gpq` of each chosen column at each chosen level.
"""

import polars as pl
import pytest

from sunnbear._core.benchmark.aggregation import (
    DEFAULT_GPQ_LEVELS,
    DERIVED_RESULTS_SCHEMA,
    add_derived_results,
    gpq_column_name,
    summarize_results,
)
from sunnbear.stats import gpq

from .results_table import results_table


def _results_of_2_solvers() -> pl.DataFrame:
    """Return the derived results of 2 solvers, 4 solves each; regula falsi fails twice, once without converging."""
    return add_derived_results(
        results_table(
            [{"solver_id": "bisection", "mc_sample_idx": idx, "n_fevals": 38 + idx} for idx in range(4)]
            + [
                {"solver_id": "regula_falsi", "mc_sample_idx": 0, "n_fevals": 6},
                {"solver_id": "regula_falsi", "mc_sample_idx": 1, "n_fevals": 9},
                {"solver_id": "regula_falsi", "mc_sample_idx": 2, "n_fevals": 12, "is_correct": False},
                {"solver_id": "regula_falsi", "mc_sample_idx": 3, "status": "max_fevals", "is_correct": False},
            ]
        )
    )


@pytest.mark.parametrize("is_lazy", [False, True])
def test_by_default_every_derived_column_is_summarized_at_the_default_levels(is_lazy):
    """The default summary keeps the frame's kind and has the group columns, the converged and correct fractions, and 1
    column per derived column and level."""
    # --- arrange ----------------------
    frame = _results_of_2_solvers()

    # --- act --------------------------
    summary = summarize_results(frame.lazy() if is_lazy else frame, "solver_id")

    # --- assert -----------------------
    assert isinstance(summary, pl.LazyFrame if is_lazy else pl.DataFrame)
    assert summary.collect_schema().names() == [
        "solver_id",
        "converged_fraction",
        "correct_fraction",
        *(gpq_column_name(column, q) for column in DERIVED_RESULTS_SCHEMA for q in DEFAULT_GPQ_LEVELS),
    ]


def test_the_rows_hold_each_group_s_fractions_and_gpq_values():
    """Each group gets its converged and correct fractions and the `gpq` of its own rows, and the groups keep their
    order of first appearance."""
    # --- act --------------------------
    summary = summarize_results(_results_of_2_solvers(), ["solver_id"])

    # --- assert -----------------------
    assert summary["solver_id"].to_list() == ["bisection", "regula_falsi"]
    assert summary["converged_fraction"].to_list() == [1.0, 0.75]
    assert summary["correct_fraction"].to_list() == [1.0, 0.5]
    assert summary["n_fevals_eff_gpq_50"].to_list() == pytest.approx(
        [gpq([38, 39, 40, 41], 0.5), gpq([6, 9, 160, 160], 0.5)]
    )


def test_each_column_is_summarized_at_its_own_levels():
    """`gpq_levels_by_column` names the columns and their levels; levels 0 and 1 give the minimum and maximum."""
    # --- act --------------------------
    summary = summarize_results(
        _results_of_2_solvers(),
        "solver_id",
        gpq_levels_by_column={"n_fevals_eff": (0.0, 1.0), "n_fevals": (0.125,)},
    )

    # --- assert -----------------------
    assert summary.columns[3:] == ["n_fevals_eff_gpq_00", "n_fevals_eff_gpq_100", "n_fevals_gpq_12.5"]
    assert summary["n_fevals_eff_gpq_00"].to_list() == [38, 6]
    assert summary["n_fevals_eff_gpq_100"].to_list() == [41, 160]


@pytest.mark.parametrize(
    "frame, gpq_levels_by_column, message",
    [
        (results_table([{}]), None, "lacks the columns .* add_derived_results first"),
        (results_table([{}]), {"no_such_column": (0.5,)}, r"lacks the columns \['no_such_column'\]\.$"),
        (results_table([{}]), {"n_fevals": (0.25, 0.25)}, "summary column name more than once"),
        (results_table([{}]), {"n_fevals": (1.5,)}, "0 <= q <= 1"),
    ],
)
def test_invalid_columns_or_levels_are_refused(frame, gpq_levels_by_column, message):
    """A missing column, a repeated level or an out-of-range level raises `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        summarize_results(frame, "solver_id", gpq_levels_by_column=gpq_levels_by_column)


@pytest.mark.parametrize(
    "q, expected",
    [(0.0, "n_fevals_gpq_00"), (0.05, "n_fevals_gpq_05"), (0.29, "n_fevals_gpq_29"), (1.0, "n_fevals_gpq_100")],
)
def test_a_gpq_column_is_named_by_its_level_in_percent(q, expected):
    """The level is written in percent with at least 2 digits, and without the floating-point rounding error of
    `q * 100`."""
    # --- act / assert -----------------
    assert gpq_column_name("n_fevals", q) == expected
