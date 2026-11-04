"""`PipelineStateStorage` holds the candidate registry and every stage's information of 1 pipeline run."""

from dataclasses import dataclass, field

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateRegistry
from .stage_information import (
    CharacterizationResults,
    DistilledSuite,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)


# ==================================================================================================
#  PipelineStateStorage
# ==================================================================================================
@dataclass
class PipelineStateStorage:
    """`PipelineStateStorage` holds the registry of a run's candidates, and 1 structure per stage for its information.

    Only the state accessors read and write the storage. A stage's structure holds its information on the candidates
    that it kept, or on those that it dropped; it is ``None``, or missing from `characterizations`, until the stage
    writes it.

    Attributes:
        registry: Every candidate, and the drop of each dropped one.
        interval_bounds: Candidate generation's interval bounds of each candidate.
        c_ranges: Validation's c-range of each valid candidate.
        characterizations: The results of each characterization stage, keyed by its `PipelineStageId`.
        nearest_kept_candidates: Spacing's nearest kept candidate of each candidate that it drops.
        edis: Full characterization's empirical difficulty index (EDI) of each candidate that it keeps.
        difficulty_classes: Core selection's difficulty class of each candidate that it receives.
        core_composition: Core selection's composition of the Core.
        suite_memberships: Distillation's place of each Core member in the suites.
        distilled_suites: Distillation's suites, the benchmark suites first, each family from its largest suite down.
    """

    registry: CandidateRegistry = field(default_factory=CandidateRegistry)
    interval_bounds: dict[ProblemId, IntervalBounds] | None = None
    c_ranges: dict[ProblemId, CRange] | None = None
    characterizations: dict[PipelineStageId, CharacterizationResults] = field(default_factory=dict)
    nearest_kept_candidates: dict[ProblemId, NearestKeptCandidate] | None = None
    edis: dict[ProblemId, float] | None = None
    difficulty_classes: dict[ProblemId, DifficultyClass] | None = None
    core_composition: CoreComposition | None = None
    suite_memberships: dict[ProblemId, SuiteMembership] | None = None
    distilled_suites: tuple[DistilledSuite, ...] | None = None
