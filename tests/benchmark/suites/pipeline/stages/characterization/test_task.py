"""`CandidateCharacterizationTask` returns, for each of its candidates in their order, a characterization result or the
reason to reject the candidate, and runs snuffled's analyses as its fidelity sets them."""

import math

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import CRange, MCSolveSettings
from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    SNUFFLED_PROPERTIES,
    DiversityFeatureFactory,
    FeatureFidelity,
)
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget
from sunnbear._core.benchmark.suites.pipeline.stages.characterization import (
    CandidateCharacterizationResult,
    CandidateCharacterizationTask,
)
from sunnbear._core.problems.core import ProblemId
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def test_the_task_returns_a_characterization_or_a_reason_per_candidate(isolated_formula_registry, monkeypatch):
    """A candidate with a simple root gets its raw features and EDI, with the evaluation counts in [2, 160], and no
    incorrect solve; f that is NaN around its root fails the solves; f that is exactly 0 around its root passes the
    solves and is rejected for its zero width; the task solves with the 2 configs that the patched
    `DiversityFeatureFactory.solver_ids` gives."""
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
    monkeypatch.setattr(DiversityFeatureFactory, "solver_ids", property(lambda self: solver_ids))
    task = CandidateCharacterizationTask(
        candidates=tuple(
            (ProblemId.from_string(problem_id), CRange(c_min=-0.5, c_max=0.5))
            for problem_id in ["f99.961", "f99.962", "f99.963"]
        ),
        fidelity=FeatureFidelity.COARSE,
    )

    # --- act --------------------------
    [characterization, reason_of_nan, reason_of_zeros] = task.run()

    # --- assert -----------------------
    assert isinstance(characterization, CandidateCharacterizationResult)
    assert characterization.raw_features.shape == (len(DiversityFeatureFactory().feature_names),)
    n_solvers_features = 2 + 9
    assert np.all(
        (characterization.raw_features[:n_solvers_features] >= 2.0)
        & (characterization.raw_features[:n_solvers_features] <= 160.0)
    )
    assert characterization.edi == characterization.raw_features[2 + 4]
    assert characterization.n_incorrect_solves_per_config == (0, 0)
    assert reason_of_nan == "function_error"
    assert reason_of_zeros == "snuffled_max_zero_width_too_large"


@pytest.mark.parametrize("fidelity", [FeatureFidelity.COARSE_DRAFT, FeatureFidelity.COARSE])
def test_the_task_runs_the_snuffled_analyses_of_its_fidelity(isolated_formula_registry, monkeypatch, fidelity):
    """The task runs `n_snuffled_analyses` analyses at the fidelity's budget, 1 at each of the first tuples of the
    shipped tuple set, in their order, and puts their properties in the snuffled features."""
    # --- arrange ----------------------
    define_formula_cls((99, 964), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    analyses = []

    def record_analysis(budget, problem, properties, *, mc_solve_settings, mc_sample_idx):
        analyses.append((budget, mc_sample_idx, float(mc_solve_settings.cs[mc_sample_idx])))
        return dict.fromkeys(properties, 0.0)

    monkeypatch.setattr(SnuffledAnalysisBudget, "extract_properties_or_rejection_reason", record_analysis)
    c_range = CRange(c_min=-0.5, c_max=0.5)
    task = CandidateCharacterizationTask(candidates=((ProblemId.from_string("f99.964"), c_range),), fidelity=fidelity)

    # --- act --------------------------
    [characterization] = task.run()

    # --- assert -----------------------
    first_v_values = fidelity.snuffled_mc_tuples.v
    assert [(budget, mc_sample_idx) for budget, mc_sample_idx, _ in analyses] == [
        (fidelity.snuffled_budget, mc_sample_idx) for mc_sample_idx in range(fidelity.n_snuffled_analyses)
    ]
    assert [c for _, _, c in analyses] == list(MCSolveSettings.map_v_onto_c_range(first_v_values, c_range))
    assert isinstance(characterization, CandidateCharacterizationResult)
    np.testing.assert_array_equal(characterization.raw_features[-len(SNUFFLED_PROPERTIES) :], 0.0)
