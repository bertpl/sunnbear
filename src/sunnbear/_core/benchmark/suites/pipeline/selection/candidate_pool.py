"""`CandidatePool` holds the input candidates of `select_diverse_suite`."""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .difficulty_class import DifficultyClass


# ==================================================================================================
#  CandidatePool
# ==================================================================================================
@dataclass(frozen=True)
class CandidatePool:
    """A `CandidatePool` holds the input candidates of `select_diverse_suite`.

    Attributes:
        vectors: The candidates' scaled full feature vectors, 1 row per candidate, as
            `FullCharacterizationStage.scaled_feature_vectors` returns them.
        edi_axis: The column of `vectors` that holds the empirical difficulty index (EDI) feature.
        difficulty_classes: Each candidate's class, in the order of `vectors`' rows.
    """

    vectors: np.ndarray
    edi_axis: int
    difficulty_classes: Sequence[DifficultyClass]

    def subset(self, rows: np.ndarray) -> "CandidatePool":
        """Return the pool of the candidates at `rows` of this pool, in the order of `rows`."""
        return CandidatePool(
            vectors=self.vectors[rows],
            edi_axis=self.edi_axis,
            difficulty_classes=[self.difficulty_classes[row] for row in rows],
        )
