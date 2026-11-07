"""`FeatureMatrix` pairs each row of a matrix of features with the `ProblemId` of its candidate."""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property

import numpy as np

from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  FeatureMatrix
# ==================================================================================================
@dataclass(frozen=True)
class FeatureMatrix:
    """A `FeatureMatrix` holds 1 feature vector per candidate, each paired with the candidate's `ProblemId`.

    A caller selects rows by their ids, with `subset`, so no caller needs to rely on a fixed order of the rows.

    Attributes:
        problem_ids: The candidates' ids, 1 per row of `values`, each once.
        values: The feature vectors, 1 row per candidate and 1 column per feature.
    """

    problem_ids: tuple[ProblemId, ...]
    values: np.ndarray

    def __post_init__(self) -> None:
        """Check that `values` is a matrix with 1 row per id, and that no id repeats.

        Raises:
            ValueError: If `values` is not 2-dimensional, if its number of rows differs from the number of ids, or if
                an id appears more than once.
        """
        if self.values.ndim != 2 or self.values.shape[0] != len(self.problem_ids):
            raise ValueError(
                f"A FeatureMatrix needs 1 row per problem id: {len(self.problem_ids)} ids for values of shape "
                f"{self.values.shape}."
            )
        elif len(self.row_index_by_problem_id) != len(self.problem_ids):
            raise ValueError("A FeatureMatrix holds each problem id once.")

    @cached_property
    def row_index_by_problem_id(self) -> dict[ProblemId, int]:
        """Return the row of each id in `values`."""
        return {problem_id: row for row, problem_id in enumerate(self.problem_ids)}

    def subset(self, problem_ids: Sequence[ProblemId]) -> "FeatureMatrix":
        """Return the matrix of the candidates `problem_ids`, in their order.

        Raises:
            KeyError: If 1 of `problem_ids` is not in the matrix.
        """
        rows = [self.row_index_by_problem_id[problem_id] for problem_id in problem_ids]
        return FeatureMatrix(problem_ids=tuple(problem_ids), values=self.values[rows])
