"""`SeriesSelectionSpec.restrict_pool` keeps the members of the spec's candidate group, or every candidate without a
group."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.benchmark_suite import PUB_SERIES
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import CandidatePool, FormulaCategoryCandidateGroup
from sunnbear._core.benchmark.suites.pipeline.stages.s6_suite_selection import SeriesSelectionSpec
from sunnbear._core.problems.catalog.c99_user_defined_functions import UserDefinedFunctions
from tests.benchmark.suites.pipeline.example_states import example_problem_ids


@pytest.mark.parametrize("has_candidate_group", [pytest.param(False, id="no_group"), pytest.param(True, id="group")])
def test_restrict_pool_keeps_the_members_of_the_candidate_group(has_candidate_group):
    """Of 2 candidates of category 99 and 3 of category 1, the group of category 99 keeps the 2; without a group, the
    pool keeps all 5."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(2) + example_problem_ids(3, category_number=1, formula_number=900)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(problem_ids), values=np.zeros((5, 2))),
        edis=np.full(5, 10.0),
        n_bisection_fevals=40,
    )
    if has_candidate_group:
        candidate_group = FormulaCategoryCandidateGroup(category=UserDefinedFunctions)
        problem_ids_expected = problem_ids[:2]
    else:
        candidate_group = None
        problem_ids_expected = problem_ids
    spec = SeriesSelectionSpec(series=PUB_SERIES, candidate_group=candidate_group)

    # --- act --------------------------
    restricted_pool = spec.restrict_pool(pool)

    # --- assert -----------------------
    assert list(restricted_pool.feature_matrix.problem_ids) == problem_ids_expected
