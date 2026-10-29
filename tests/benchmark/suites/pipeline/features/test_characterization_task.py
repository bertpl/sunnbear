"""`CandidateCharacterizationTask` maps the solves' evaluation counts onto [0, 1] on a log scale, and returns a feature
vector or the reason to reject each candidate, in the order of its candidates."""

import math

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import RejectionReason
from sunnbear._core.benchmark.suites.pipeline.features import CandidateCharacterizationTask, FeatureFidelity
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


@pytest.mark.parametrize(
    "value, normalized_expected",
    [
        pytest.param(2, 0.0, id="minimum_of_a_correct_solve"),
        pytest.param(40, math.log(20) / math.log(80), id="bisection_count"),
        pytest.param(160, 1.0, id="evaluation_budget"),
    ],
)
def test_the_normalization_maps_2_to_0_and_max_fevals_to_1_on_a_log_scale(value, normalized_expected):
    """With `max_fevals` 160, a count maps onto ``log(count / 2) / log(80)``."""
    # --- act --------------------------
    normalized = CandidateCharacterizationTask._normalize_n_fevals_eff(value, 160)

    # --- assert -----------------------
    assert normalized == pytest.approx(normalized_expected)


def test_the_task_returns_a_feature_vector_or_a_reason_per_candidate(isolated_formula_registry):
    """A simple root gets its feature vector, each value in [0, 1]; f that is NaN around its root fails the solves; f
    that is exactly 0 around its root passes the solves and fails snuffled's zero width rule."""
    # --- arrange ----------------------
    root_offset = 1 / 3
    define_formula_cls((99, 961), lambda x, c: x - c - root_offset, -1.0, 1.0)
    define_formula_cls(
        (99, 962), lambda x, c: math.nan if abs(x - c - root_offset) < 0.1 else x - c - root_offset, -1.0, 1.0
    )
    define_formula_cls(
        (99, 963), lambda x, c: 0.0 if abs(x - c - root_offset) < 1e-6 else x - c - root_offset, -1.0, 1.0
    )
    solver_ids = ("brent[variant='inverse_quadratic']", "illinois")
    task = CandidateCharacterizationTask(
        candidates=tuple((problem_id, -0.5, 0.5) for problem_id in ["f99.961", "f99.962", "f99.963"]),
        solver_ids=solver_ids,
        fidelity=FeatureFidelity.COARSE,
    )

    # --- act --------------------------
    [features, reason_of_nan, reason_of_zeros] = task.run()

    # --- assert -----------------------
    assert isinstance(features, dict)
    assert list(features) == FeatureFidelity.COARSE.feature_column_names(solver_ids)
    assert all(0.0 <= value <= 1.0 for value in features.values())
    assert reason_of_nan is RejectionReason.FUNCTION_ERROR
    assert reason_of_zeros is RejectionReason.SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE
