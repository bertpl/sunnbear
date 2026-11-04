"""`FeatureMatrix` refuses values that do not hold 1 row per problem id, and a problem id that repeats."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.problems.core import ProblemId


@pytest.mark.parametrize(
    "problem_ids, shape, message",
    [
        (("f99.1", "f99.2"), (3, 4), "1 row per problem id"),
        (("f99.1", "f99.2"), (2,), "1 row per problem id"),
        (("f99.1", "f99.1"), (2, 4), "each problem id once"),
    ],
)
def test_the_matrix_refuses_rows_that_do_not_match_the_ids(problem_ids: tuple[str, ...], shape: tuple, message: str):
    """The matrix refuses values without 1 row per problem id, and a problem id that repeats."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        FeatureMatrix(problem_ids=tuple(map(ProblemId.from_string, problem_ids)), values=np.zeros(shape))


def test_a_subset_holds_the_rows_of_the_given_ids_in_their_order():
    """The subset of 2 of 3 rows, in reverse order, pairs each id with its own row; an id outside the matrix is
    refused."""
    # --- arrange ----------------------
    problem_ids = tuple(ProblemId.from_string(f"f99.{idx}") for idx in (1, 2, 3))
    matrix = FeatureMatrix(problem_ids=problem_ids, values=np.arange(6.0).reshape(3, 2))

    # --- act --------------------------
    subset = matrix.subset([problem_ids[2], problem_ids[0]])

    # --- assert -----------------------
    assert subset.problem_ids == (problem_ids[2], problem_ids[0])
    np.testing.assert_array_equal(subset.values, [[4.0, 5.0], [0.0, 1.0]])
    with pytest.raises(KeyError):
        matrix.subset([ProblemId.from_string("f99.4")])
