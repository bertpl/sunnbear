"""The value objects in which the stages of the benchmark suite pipeline hand their information to the state.

Each stage's state accessor takes and gives the stage's information in these objects and in plain mappings keyed by
`ProblemId`; the information of the other stages is in objects of other packages, such as `CRange`, `DifficultyClass`
and `CoreComposition`.
"""

from collections.abc import Mapping
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
        n_incorrect_solves: For each kept candidate, the number of solves without a correct answer of each core
            solver config, in the order of `definition.solver_ids`. Each config solves each candidate
            `fidelity.solver_mc_size` times.
    """

    definition: DiversityFeatureFactory
    fidelity: FeatureFidelity
    raw_feature_matrix: FeatureMatrix
    block_scales: FeatureBlockScales | None
    n_incorrect_solves: Mapping[ProblemId, tuple[int, ...]]


# ==================================================================================================
#  NearestKeptCandidate
# ==================================================================================================
@dataclass(frozen=True)
class NearestKeptCandidate:
    """A `NearestKeptCandidate` names the kept candidate of the same formula nearest to a candidate that spacing drops.

    Attributes:
        problem_id: The id of the nearest kept candidate.
        distance: The distance between the 2 candidates, in the units of spacing's minimum distance.
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
#  DistilledSuite
# ==================================================================================================
@dataclass(frozen=True)
class DistilledSuite:
    """A `DistilledSuite` describes 1 suite that distillation selects.

    Attributes:
        suite_family: The suite's `SuiteFamily`.
        size: The suite's number of candidates.
        diversity: The diversity score of the max-div run that selected the suite; ``None`` for the largest
            calibration suite, which no run selects.
    """

    suite_family: SuiteFamily
    size: int
    diversity: float | None
