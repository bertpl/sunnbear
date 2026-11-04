"""`FeatureMatrix` refuses values that do not hold 1 row per problem id, and a problem id that repeats."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.features import FeatureMatrix
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
    """3 rows for 2 ids, a 1-dimensional array, and a repeated id are refused."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        FeatureMatrix(problem_ids=tuple(map(ProblemId.from_string, problem_ids)), values=np.zeros(shape))
