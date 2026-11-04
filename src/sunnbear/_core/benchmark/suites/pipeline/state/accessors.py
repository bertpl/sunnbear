"""The state accessors, 1 class per stage of the benchmark suite pipeline: all that a stage sees of the state.

`PipelineStateAccessor` is the base class of every accessor. An accessor reads and writes the `PipelineStateStorage` of
the run, and is the contract that its stage adheres to:

- it gives the ids of the candidates that no stage has dropped, and the information of earlier stages on those
  candidates only;
- it writes its stage's information once, and refuses information on any other set of candidates than the one that
  the write's docstring names;
- it takes its stage's drops, through `PipelineStateAccessor.reject` for an invalid candidate and
  `PipelineStateAccessor.drop` for a valid one that the stage does not keep.

The 2 characterization stages share `CharacterizationStateAccessor`, and core selection and distillation share
`SelectionStateAccessor`, because each pair reads and writes the same kind of information.
"""

from collections.abc import Collection, Mapping, Sequence
from typing import ClassVar

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import CandidatePool, CoreComposition, DifficultyClass
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateDrop
from .stage_information import (
    CharacterizationResults,
    DistilledSuite,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)
from .storage import PipelineStateStorage


# ==================================================================================================
#  PipelineStateAccessor
# ==================================================================================================
class PipelineStateAccessor:
    """A `PipelineStateAccessor` gives 1 stage the candidates that no stage has dropped, and takes the stage's drops.

    Class attributes:
        stage_id: The `PipelineStageId` of the accessor's stage.
    """

    stage_id: ClassVar[PipelineStageId]

    def __init__(self, storage: PipelineStateStorage) -> None:
        """Create the accessor of the run whose information `storage` holds."""
        self._storage = storage

    @property
    def problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of the candidates that no stage has dropped, in the order of candidate generation."""
        return self._storage.registry.remaining_problem_ids

    def reject(self, problem_id: ProblemId, reason: str) -> None:
        """Drop the candidate `problem_id` as invalid, for `reason`.

        Raises:
            ValueError: If `problem_id` is not a candidate that no stage has dropped.
        """
        self._record_drop(problem_id, reason, is_rejection=True)

    def drop(self, problem_id: ProblemId, reason: str) -> None:
        """Drop the valid candidate `problem_id`, which the stage does not keep, for `reason`.

        Raises:
            ValueError: If `problem_id` is not a candidate that no stage has dropped.
        """
        self._record_drop(problem_id, reason, is_rejection=False)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _record_drop(self, problem_id: ProblemId, reason: str, *, is_rejection: bool) -> None:
        """Record the drop of `problem_id` by this accessor's stage."""
        self._storage.registry.record_drop(
            problem_id, CandidateDrop(stage_id=self.stage_id, reason=reason, is_rejection=is_rejection)
        )

    def _check_written_once(self, *, is_written: bool) -> None:
        """Check that a piece of the stage's information is not written yet.

        Raises:
            ValueError: If the information `is_written` already.
        """
        if is_written:
            raise ValueError(f"{type(self).__name__} writes each piece of its stage's information once.")

    def _check_covers(self, problem_ids: Collection[ProblemId], expected: Collection[ProblemId]) -> None:
        """Check that a write's information covers the candidates `expected`, no more and no fewer.

        Raises:
            ValueError: If `problem_ids` differs from `expected`.
        """
        n_unexpected = len(set(problem_ids) - set(expected))
        n_missing = len(set(expected) - set(problem_ids))
        if n_unexpected or n_missing:
            raise ValueError(
                f"{type(self).__name__} takes information on {len(expected)} candidates: {n_unexpected} other "
                f"candidates given, {n_missing} missing."
            )

    def _restrict_to_remaining[V](self, information: Mapping[ProblemId, V]) -> dict[ProblemId, V]:
        """Return the entries of `information` of the candidates that no stage has dropped, in their order."""
        return {problem_id: information[problem_id] for problem_id in self.problem_ids}


# ==================================================================================================
#  CandidateGenerationStateAccessor
# ==================================================================================================
class CandidateGenerationStateAccessor(PipelineStateAccessor):
    """`CandidateGenerationStateAccessor` takes the run's candidates."""

    stage_id = PipelineStageId.CANDIDATE_GENERATION

    def add_candidates(self, interval_bounds: Mapping[ProblemId, IntervalBounds]) -> None:
        """Register the candidates of `interval_bounds`, in its order, with their interval bounds.

        Raises:
            ValueError: If the candidates were added before.
        """
        self._check_written_once(is_written=self._storage.interval_bounds is not None)
        self._storage.registry.add(list(interval_bounds))
        self._storage.interval_bounds = dict(interval_bounds)


# ==================================================================================================
#  CandidateValidationStateAccessor
# ==================================================================================================
class CandidateValidationStateAccessor(PipelineStateAccessor):
    """`CandidateValidationStateAccessor` gives the candidates' interval bounds, and takes the valid ones' c-ranges."""

    stage_id = PipelineStageId.CANDIDATE_VALIDATION

    def interval_bounds(self) -> dict[ProblemId, IntervalBounds]:
        """Return each candidate's interval bounds."""
        return self._restrict_to_remaining(self._storage.interval_bounds or {})

    def set_c_ranges(self, c_ranges: Mapping[ProblemId, CRange]) -> None:
        """Store the c-range of each candidate that no stage has dropped, after the stage's rejections.

        Raises:
            ValueError: If the c-ranges were stored before, or do not cover exactly those candidates.
        """
        self._check_written_once(is_written=self._storage.c_ranges is not None)
        self._check_covers(c_ranges.keys(), self.problem_ids)
        self._storage.c_ranges = self._restrict_to_remaining(c_ranges)


# ==================================================================================================
#  CharacterizationStateAccessor
# ==================================================================================================
class CharacterizationStateAccessor(PipelineStateAccessor):
    """`CharacterizationStateAccessor` gives the candidates' c-ranges, and takes a characterization stage's results."""

    def c_ranges(self) -> dict[ProblemId, CRange]:
        """Return each candidate's c-range."""
        return self._restrict_to_remaining(self._storage.c_ranges or {})

    def set_characterization_results(self, results: CharacterizationResults) -> None:
        """Store the stage's results on each candidate that no stage has dropped, after the stage's rejections.

        Raises:
            ValueError: If the results were stored before, or their raw features or incorrect solves do not cover
                exactly those candidates.
        """
        self._check_written_once(is_written=self.stage_id in self._storage.characterizations)
        self._check_covers(results.raw_feature_matrix.problem_ids, self.problem_ids)
        self._check_covers(results.n_incorrect_solves.keys(), self.problem_ids)
        self._storage.characterizations[self.stage_id] = results


# ==================================================================================================
#  CoarseCharacterizationStateAccessor
# ==================================================================================================
class CoarseCharacterizationStateAccessor(CharacterizationStateAccessor):
    """`CoarseCharacterizationStateAccessor` is the state accessor of coarse characterization."""

    stage_id = PipelineStageId.COARSE_CHARACTERIZATION


# ==================================================================================================
#  SpacingStateAccessor
# ==================================================================================================
class SpacingStateAccessor(PipelineStateAccessor):
    """`SpacingStateAccessor` gives the coarse features, and takes the nearest kept candidate of each dropped one."""

    stage_id = PipelineStageId.SPACING

    def coarse_scaled_feature_matrix(self) -> FeatureMatrix | None:
        """Return the scaled matrix of the coarse features, or ``None`` if coarse characterization has no scales.

        Coarse characterization has no scales when it kept fewer than 2 candidates.
        """
        results = self._storage.characterizations[PipelineStageId.COARSE_CHARACTERIZATION]
        if results.block_scales is None:
            return None
        else:
            raw_feature_matrix = results.raw_feature_matrix.subset(self.problem_ids)
            return results.definition.build_scaled_matrix(raw_feature_matrix, results.block_scales)

    def set_nearest_kept_candidates(self, nearest_kept_candidates: Mapping[ProblemId, NearestKeptCandidate]) -> None:
        """Store the nearest kept candidate of each candidate that the stage dropped, after the stage's drops.

        Raises:
            ValueError: If they were stored before, or do not cover exactly the candidates that the stage dropped.
        """
        self._check_written_once(is_written=self._storage.nearest_kept_candidates is not None)
        self._check_covers(nearest_kept_candidates.keys(), self._storage.registry.problem_ids_dropped_by(self.stage_id))
        self._storage.nearest_kept_candidates = dict(nearest_kept_candidates)


# ==================================================================================================
#  FullCharacterizationStateAccessor
# ==================================================================================================
class FullCharacterizationStateAccessor(CharacterizationStateAccessor):
    """`FullCharacterizationStateAccessor` takes full characterization's results, and each candidate's EDI."""

    stage_id = PipelineStageId.FULL_CHARACTERIZATION

    def set_edis(self, edis: Mapping[ProblemId, float]) -> None:
        """Store the EDI of each candidate that no stage has dropped, after the stage's rejections.

        Raises:
            ValueError: If the EDIs were stored before, or do not cover exactly those candidates.
        """
        self._check_written_once(is_written=self._storage.edis is not None)
        self._check_covers(edis.keys(), self.problem_ids)
        self._storage.edis = self._restrict_to_remaining(edis)


# ==================================================================================================
#  SelectionStateAccessor
# ==================================================================================================
class SelectionStateAccessor(PipelineStateAccessor):
    """`SelectionStateAccessor` gives the candidates of a selection by max-div, as a `CandidatePool`."""

    def candidate_pool(self) -> CandidatePool:
        """Return the pool of the candidates that no stage has dropped: their scaled full features, EDIs and classes.

        Raises:
            ValueError: If the difficulty classes are not stored yet, or full characterization has no scales, because
                it kept fewer than 2 candidates.
        """
        results = self._storage.characterizations[PipelineStageId.FULL_CHARACTERIZATION]
        if self._storage.difficulty_classes is None:
            raise ValueError("The candidate pool needs the difficulty classes, which core selection stores.")
        elif results.block_scales is None:
            raise ValueError("The candidate pool needs the scales of full characterization, which has none.")
        else:
            raw_feature_matrix = results.raw_feature_matrix.subset(self.problem_ids)
            return CandidatePool.from_candidates(
                results.definition.build_scaled_matrix(raw_feature_matrix, results.block_scales),
                edis=self._storage.edis or {},
                difficulty_classes=self._storage.difficulty_classes,
            )


# ==================================================================================================
#  CoreSelectionStateAccessor
# ==================================================================================================
class CoreSelectionStateAccessor(SelectionStateAccessor):
    """`CoreSelectionStateAccessor` gives the candidates' EDIs, and takes their classes and the Core's composition."""

    stage_id = PipelineStageId.CORE_SELECTION

    def edis(self) -> dict[ProblemId, float]:
        """Return each candidate's EDI."""
        return self._restrict_to_remaining(self._storage.edis or {})

    def set_difficulty_classes(self, difficulty_classes: Mapping[ProblemId, DifficultyClass]) -> None:
        """Store the class of each candidate that no stage has dropped, before the stage's drops.

        Raises:
            ValueError: If the classes were stored before, or do not cover exactly those candidates.
        """
        self._check_written_once(is_written=self._storage.difficulty_classes is not None)
        self._check_covers(difficulty_classes.keys(), self.problem_ids)
        self._storage.difficulty_classes = self._restrict_to_remaining(difficulty_classes)

    def set_core_composition(self, core_composition: CoreComposition) -> None:
        """Store the Core's composition.

        Raises:
            ValueError: If the composition was stored before.
        """
        self._check_written_once(is_written=self._storage.core_composition is not None)
        self._storage.core_composition = core_composition


# ==================================================================================================
#  DistillationStateAccessor
# ==================================================================================================
class DistillationStateAccessor(SelectionStateAccessor):
    """`DistillationStateAccessor` gives the Core's composition, and takes the suites distilled from the Core."""

    stage_id = PipelineStageId.DISTILLATION

    def core_composition(self) -> CoreComposition:
        """Return the Core's composition, which core selection stored.

        Raises:
            ValueError: If core selection stored no composition.
        """
        if self._storage.core_composition is None:
            raise ValueError("Core selection stored no Core composition.")
        else:
            return self._storage.core_composition

    def set_suite_memberships(self, suite_memberships: Mapping[ProblemId, SuiteMembership]) -> None:
        """Store the suite membership of each Core member, that is each candidate that no stage has dropped.

        Raises:
            ValueError: If the memberships were stored before, or do not cover exactly those candidates.
        """
        self._check_written_once(is_written=self._storage.suite_memberships is not None)
        self._check_covers(suite_memberships.keys(), self.problem_ids)
        self._storage.suite_memberships = self._restrict_to_remaining(suite_memberships)

    def set_distilled_suites(self, distilled_suites: Sequence[DistilledSuite]) -> None:
        """Store the distilled suites, the benchmark suites first, each family from its largest suite down.

        Raises:
            ValueError: If the suites were stored before.
        """
        self._check_written_once(is_written=self._storage.distilled_suites is not None)
        self._storage.distilled_suites = tuple(distilled_suites)
