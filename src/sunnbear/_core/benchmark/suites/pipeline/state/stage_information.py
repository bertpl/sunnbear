"""The value objects of this module carry each pipeline stage's information to and from the stage's state accessor.

Each stage's state accessor takes and gives the stage's information in these objects and in plain mappings keyed by
`ProblemId`; a stage whose information has a type of its own in another package, such as `CRange`, `DifficultyClass`
or `CoreComposition`, uses that type.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import NamedTuple

from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    FeatureBlockScales,
    FeatureFidelity,
    FeatureMatrix,
    DiversityFeatureFactory,
)
from sunnbear._core.benchmark.suites.pipeline.selection import SuiteFamily
from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  IntervalBounds
# ==================================================================================================
class IntervalBounds(NamedTuple):
    """`IntervalBounds` holds a candidate's interval bounds ``a`` and ``b``, as candidate generation finds them."""

    a: float
    b: float


# ==================================================================================================
#  CharacterizationResults
# ==================================================================================================
@dataclass(frozen=True)
class CharacterizationResults:
    """`CharacterizationResults` holds what 1 characterization stage computed for the candidates that it keeps.

    Attributes:
        definition: The `DiversityFeatureFactory` of the feature vectors.
        fidelity: The `FeatureFidelity` of the stage's solves and analyses.
        raw_feature_matrix: The raw features of each kept candidate.
        block_scales: The scale of each block over the kept candidates; ``None`` when the stage keeps fewer than 2.
        n_incorrect_solves_per_config: For each kept candidate, 1 count per core solver config, in the order of
            `definition.solver_ids`: the number of that config's solves that gave no correct answer. Each config
            solves each candidate `fidelity.solver_mc_size` times.
    """

    definition: DiversityFeatureFactory
    fidelity: FeatureFidelity
    raw_feature_matrix: FeatureMatrix
    block_scales: FeatureBlockScales | None
    n_incorrect_solves_per_config: Mapping[ProblemId, tuple[int, ...]]

    def build_scaled_feature_matrix(self, problem_ids: Sequence[ProblemId]) -> FeatureMatrix | None:
        """Return the scaled features of the candidates `problem_ids`; ``None`` when the stage has no block scales."""
        if self.block_scales is None:
            return None
        else:
            return self.definition.build_scaled_matrix(self.raw_feature_matrix.subset(problem_ids), self.block_scales)


# ==================================================================================================
#  NearestKeptCandidate
# ==================================================================================================
@dataclass(frozen=True)
class NearestKeptCandidate:
    """For a candidate that spacing drops, `NearestKeptCandidate` names the nearest kept candidate of the same formula.

    Attributes:
        problem_id: The id of the nearest kept candidate.
        distance: The distance between the 2 candidates, as a multiple of spacing's minimum distance.
    """

    problem_id: ProblemId
    distance: float


# ==================================================================================================
#  SuiteMembership
# ==================================================================================================
@dataclass(frozen=True)
class SuiteMembership:
    """A `SuiteMembership` places a Core member in the suites that distillation selects.

    Attributes:
        suite_family: The member's `SuiteFamily`.
        smallest_containing_suite_size: The size of the smallest suite of that family that holds the member; every
            larger suite of the family holds it too.
    """

    suite_family: SuiteFamily
    smallest_containing_suite_size: int


# ==================================================================================================
#  DistilledSuiteSummary
# ==================================================================================================
@dataclass(frozen=True)
class DistilledSuiteSummary:
    """A `DistilledSuiteSummary` gives the family, size and diversity score of 1 suite that distillation selects.

    Attributes:
        suite_family: The suite's `SuiteFamily`.
        size: The suite's number of candidates.
        diversity: The diversity score of the max-div run that selected the suite; ``None`` for the largest
            calibration suite, which no run selects.
    """

    suite_family: SuiteFamily
    size: int
    diversity: float | None
