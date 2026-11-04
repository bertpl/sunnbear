"""`CandidateCharacterizationTask` returns, for each of its candidates in their order, a characterization result or the
reason to reject the candidate."""

import math

import numpy as np

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity, DiversityFeatureFactory
from sunnbear._core.benchmark.suites.pipeline.stages.characterization import (
    CandidateCharacterizationResult,
    CandidateCharacterizationTask,
)
from sunnbear._core.problems.core import ProblemId
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def test_the_task_returns_a_characterization_or_a_reason_per_candidate(isolated_formula_registry):
    """A candidate with a simple root gets its raw features and EDI, with the evaluation counts in [2, 160], and no
    incorrect solve; f that is NaN around its root fails the solves; f that is exactly 0 around its root passes the
    solves and is rejected for its zero width."""
    # --- arrange ----------------------
    root_offset = 1 / 3
    define_formula_cls((99, 961), lambda x, c: x - c - root_offset, -1.0, 1.0)
    define_formula_cls(
        (99, 962), lambda x, c: math.nan if abs(x - c - root_offset) < 0.1 else x - c - root_offset, -1.0, 1.0
    )
    define_formula_cls(
        (99, 963), lambda x, c: 0.0 if abs(x - c - root_offset) < 1e-6 else x - c - root_offset, -1.0, 1.0
    )
    definition = DiversityFeatureFactory(solver_ids=("brent[variant='inverse_quadratic']", "illinois"))
    task = CandidateCharacterizationTask(
        candidates=tuple(
            (ProblemId.from_string(problem_id), CRange(c_min=-0.5, c_max=0.5))
            for problem_id in ["f99.961", "f99.962", "f99.963"]
        ),
        definition=definition,
        fidelity=FeatureFidelity.COARSE,
    )

    # --- act --------------------------
    [characterization, reason_of_nan, reason_of_zeros] = task.run()

    # --- assert -----------------------
    assert isinstance(characterization, CandidateCharacterizationResult)
    assert characterization.raw_features.shape == (len(definition.feature_names),)
    n_solvers_features = 2 + 9
    assert np.all(
        (characterization.raw_features[:n_solvers_features] >= 2.0)
        & (characterization.raw_features[:n_solvers_features] <= 160.0)
    )
    assert characterization.edi == characterization.raw_features[2 + 4]
    assert characterization.n_incorrect_solves_per_config == (0, 0)
    assert reason_of_nan == "function_error"
    assert reason_of_zeros == "snuffled_max_zero_width_too_large"
