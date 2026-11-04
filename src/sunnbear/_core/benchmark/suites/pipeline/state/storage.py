"""`PipelineStateStorage` holds the candidate registry and every stage's information of 1 pipeline run."""

from dataclasses import dataclass, field

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateRegistry
from .stage_information import (
    CharacterizationResults,
    DistilledSuiteSummary,
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

    Only the state accessors read and write the storage. Each attribute below names the candidates that its stage's
    structure holds information on; a structure is ``None``, or missing from `characterization_results`, until its
    stage writes the structure.

    Attributes:
        candidate_registry: Every candidate, and the drop of each dropped one.
        interval_bounds: Candidate generation's interval bounds of each candidate.
        c_ranges: Validation's c-range of each valid candidate.
        characterization_results: The results of each characterization stage, keyed by its `PipelineStageId`.
        nearest_kept_candidates: Spacing's nearest kept candidate of each candidate that it drops.
        edis: Full characterization's empirical difficulty index (EDI) of each candidate that it keeps.
        difficulty_classes: Core selection's difficulty class of each candidate that it receives.
        core_composition: Core selection's composition of the Core.
        suite_memberships: Distillation's `SuiteMembership` of each Core member.
        distilled_suite_summaries: Distillation's `DistilledSuiteSummary` of each suite, in the order that
            `DistillationStateAccessor.set_distilled_suite_summaries` states.
    """

    candidate_registry: CandidateRegistry = field(default_factory=CandidateRegistry)
    interval_bounds: dict[ProblemId, IntervalBounds] | None = None
    c_ranges: dict[ProblemId, CRange] | None = None
    characterization_results: dict[PipelineStageId, CharacterizationResults] = field(default_factory=dict)
    nearest_kept_candidates: dict[ProblemId, NearestKeptCandidate] | None = None
    edis: dict[ProblemId, float] | None = None
    difficulty_classes: dict[ProblemId, DifficultyClass] | None = None
    core_composition: CoreComposition | None = None
    suite_memberships: dict[ProblemId, SuiteMembership] | None = None
    distilled_suite_summaries: tuple[DistilledSuiteSummary, ...] | None = None
