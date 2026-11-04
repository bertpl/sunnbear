"""`FeatureMatrix` pairs each row of a matrix of features with the `ProblemId` of its candidate."""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  FeatureMatrix
# ==================================================================================================
@dataclass(frozen=True)
class FeatureMatrix:
    """A `FeatureMatrix` holds 1 feature vector per candidate, each paired with the candidate's `ProblemId`.

    A caller finds a candidate's row by its id, so no caller needs to know the order of the rows.

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
        elif len(set(self.problem_ids)) != len(self.problem_ids):
            raise ValueError("A FeatureMatrix holds each problem id once.")
