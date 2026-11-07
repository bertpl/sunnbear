"""This module defines the state accessors, 1 class per stage of the benchmark suite pipeline.

A stage sees the state only through its accessor. `PipelineStateAccessor` is the base class of every accessor. An
accessor reads and writes the `PipelineStateStorage` of the run, and is the contract that its stage adheres to:

- it gives the ids of the candidates that no stage has dropped, and the information of earlier stages on those
  candidates only;
- it writes its stage's information once, and raises `ValueError` when that information covers other candidates than
  the ones that the writing method's docstring names;
- it takes its stage's drops, through `PipelineStateAccessor.reject` for an invalid candidate and
  `PipelineStateAccessor.drop` for a valid one that the stage does not keep.

The 2 characterization stages share `CharacterizationStateAccessor`, and core selection and distillation share
`SelectionStateAccessor`, because each pair reads and writes the same kind of information.
"""

from collections.abc import Collection, Mapping
from typing import ClassVar

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import CandidatePool, DifficultyTier
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateDrop
from .stage_information import CharacterizationResults, IntervalBounds, NearestKeptCandidate, SuiteSelectionDetails
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
    def remaining_problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of the candidates that no stage has dropped, in the order of candidate generation."""
        return self._storage.candidate_registry.remaining_problem_ids

    def reject(self, problem_id: ProblemId, reason: str) -> None:
        """Drop the candidate `problem_id` as invalid, for `reason`.

        Raises:
            ValueError: If `problem_id` is not a candidate of the run, or a stage has dropped it already.
        """
        self._storage.candidate_registry.record_drop(
            problem_id, CandidateDrop(stage_id=self.stage_id, reason=reason, is_rejection=True)
        )

    def drop(self, problem_id: ProblemId, reason: str) -> None:
        """Drop the valid candidate `problem_id`, which the stage does not keep, for `reason`.

        Raises:
            ValueError: If `problem_id` is not a candidate of the run, or a stage has dropped it already.
        """
        self._storage.candidate_registry.record_drop(
            problem_id, CandidateDrop(stage_id=self.stage_id, reason=reason, is_rejection=False)
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _check_not_written(self, *, is_written: bool) -> None:
        """Check that a piece of the stage's information is not written yet.

        Raises:
            ValueError: If `is_written` is true.
        """
        if is_written:
            raise ValueError(f"{type(self).__name__} writes each piece of its stage's information once.")

    def _check_covers(self, problem_ids: Collection[ProblemId], expected_problem_ids: Collection[ProblemId]) -> None:
        """Check that the information to be written covers the candidates `expected_problem_ids`, no more and no fewer.

        Raises:
            ValueError: If `problem_ids` differs from `expected_problem_ids`.
        """
        n_unexpected = len(set(problem_ids) - set(expected_problem_ids))
        n_missing = len(set(expected_problem_ids) - set(problem_ids))
        if n_unexpected or n_missing:
            raise ValueError(
                f"{type(self).__name__} takes information on {len(expected_problem_ids)} candidates: {n_unexpected} "
                f"other candidates given, {n_missing} missing."
            )

    def _restrict_to_remaining[V](self, information: Mapping[ProblemId, V]) -> dict[ProblemId, V]:
        """Return the entries of `information` for the candidates that no stage has dropped, in the registry's order."""
        return {problem_id: information[problem_id] for problem_id in self.remaining_problem_ids}


# ==================================================================================================
#  CandidateGenerationStateAccessor
# ==================================================================================================
class CandidateGenerationStateAccessor(PipelineStateAccessor):
    """`CandidateGenerationStateAccessor` registers the run's candidates."""

    stage_id = PipelineStageId.CANDIDATE_GENERATION

    def add_candidates(self, interval_bounds: Mapping[ProblemId, IntervalBounds]) -> None:
        """Register the candidates of `interval_bounds`, in its order, with their interval bounds.

        Raises:
            ValueError: If the candidates were added before.
        """
        self._check_not_written(is_written=self._storage.interval_bounds is not None)
        self._storage.candidate_registry.add(list(interval_bounds))
        self._storage.interval_bounds = dict(interval_bounds)


# ==================================================================================================
#  CandidateValidationStateAccessor
# ==================================================================================================
class CandidateValidationStateAccessor(PipelineStateAccessor):
    """`CandidateValidationStateAccessor` gives the candidates' interval bounds, and takes the valid ones' c-ranges."""

    stage_id = PipelineStageId.CANDIDATE_VALIDATION

    def interval_bounds(self) -> dict[ProblemId, IntervalBounds]:
        """Return the interval bounds of each candidate that no stage has dropped."""
        return self._restrict_to_remaining(self._storage.interval_bounds or {})

    def set_c_ranges(self, c_ranges: Mapping[ProblemId, CRange]) -> None:
        """Store the c-range of each candidate that no stage has dropped.

        The stage calls this after it has recorded its rejections.

        Raises:
            ValueError: If the c-ranges were stored before, or do not cover exactly those candidates.
        """
        self._check_not_written(is_written=self._storage.c_ranges is not None)
        self._check_covers(c_ranges.keys(), self.remaining_problem_ids)
        self._storage.c_ranges = self._restrict_to_remaining(c_ranges)


# ==================================================================================================
#  CharacterizationStateAccessor
# ==================================================================================================
class CharacterizationStateAccessor(PipelineStateAccessor):
    """`CharacterizationStateAccessor` gives the candidates' c-ranges, and takes a characterization stage's results."""

    def c_ranges(self) -> dict[ProblemId, CRange]:
        """Return the c-range of each candidate that no stage has dropped."""
        return self._restrict_to_remaining(self._storage.c_ranges or {})

    def set_characterization_results(self, results: CharacterizationResults) -> None:
        """Store the stage's results on each candidate that no stage has dropped.

        The stage calls this after it has recorded its rejections.

        Raises:
            ValueError: If the results were stored before, or their raw features or incorrect solves do not cover
                exactly those candidates.
        """
        self._check_not_written(is_written=self.stage_id in self._storage.characterization_results)
        self._check_covers(results.raw_feature_matrix.problem_ids, self.remaining_problem_ids)
        self._check_covers(results.n_incorrect_solves_per_config.keys(), self.remaining_problem_ids)
        self._storage.characterization_results[self.stage_id] = results


# ==================================================================================================
#  CoarseCharacterizationStateAccessor
# ==================================================================================================
class CoarseCharacterizationStateAccessor(CharacterizationStateAccessor):
    """`CoarseCharacterizationStateAccessor` gives the candidates' c-ranges, and takes the stage's results."""

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
        results = self._storage.characterization_results[PipelineStageId.COARSE_CHARACTERIZATION]
        return results.build_scaled_feature_matrix(self.remaining_problem_ids)

    def set_nearest_kept_candidates(self, nearest_kept_candidates: Mapping[ProblemId, NearestKeptCandidate]) -> None:
        """Store the nearest kept candidate of each candidate that the stage dropped.

        The stage calls this after it has recorded its drops.

        Raises:
            ValueError: If the nearest kept candidates were stored before, or do not cover exactly the candidates that
                the stage dropped.
        """
        self._check_not_written(is_written=self._storage.nearest_kept_candidates is not None)
        self._check_covers(
            nearest_kept_candidates.keys(), self._storage.candidate_registry.problem_ids_dropped_by(self.stage_id)
        )
        self._storage.nearest_kept_candidates = dict(nearest_kept_candidates)


# ==================================================================================================
#  FullCharacterizationStateAccessor
# ==================================================================================================
class FullCharacterizationStateAccessor(CharacterizationStateAccessor):
    """`FullCharacterizationStateAccessor` takes the stage's results and empirical difficulty indices (EDIs)."""

    stage_id = PipelineStageId.FULL_CHARACTERIZATION

    def set_edis(self, edis: Mapping[ProblemId, float]) -> None:
        """Store the EDI of each candidate that no stage has dropped.

        The stage calls this after it has recorded its rejections.

        Raises:
            ValueError: If the EDIs were stored before, or do not cover exactly those candidates.
        """
        self._check_not_written(is_written=self._storage.edis is not None)
        self._check_covers(edis.keys(), self.remaining_problem_ids)
        self._storage.edis = self._restrict_to_remaining(edis)


# ==================================================================================================
#  SelectionStateAccessor
# ==================================================================================================
class SelectionStateAccessor(PipelineStateAccessor):
    """`SelectionStateAccessor` gives the input candidates of max-div's selection, as a `CandidatePool`."""

    def candidate_pool(self) -> CandidatePool:
        """Return the pool of the candidates that no stage has dropped.

        The pool holds their scaled features from full characterization, their EDIs and their difficulty tiers.

        Raises:
            ValueError: If the difficulty tiers are not stored yet, or full characterization has no scales, because it
                kept fewer than 2 candidates.
        """
        results = self._storage.characterization_results[PipelineStageId.FULL_CHARACTERIZATION]
        scaled_feature_matrix = results.build_scaled_feature_matrix(self.remaining_problem_ids)
        if self._storage.difficulty_tiers is None:
            raise ValueError("The candidate pool needs the difficulty tiers, which core selection stores.")
        elif scaled_feature_matrix is None:
            raise ValueError("The candidate pool needs the scales of full characterization, which has none.")
        else:
            return CandidatePool.from_feature_matrix(
                scaled_feature_matrix,
                edis=self._storage.edis or {},
                difficulty_tiers=self._storage.difficulty_tiers,
            )


# ==================================================================================================
#  CoreSelectionStateAccessor
# ==================================================================================================
class CoreSelectionStateAccessor(SelectionStateAccessor):
    """`CoreSelectionStateAccessor` gives the candidates' EDIs, and takes their tiers and the Core's details."""

    stage_id = PipelineStageId.CORE_SELECTION

    def edis(self) -> dict[ProblemId, float]:
        """Return the EDI of each candidate that no stage has dropped."""
        return self._restrict_to_remaining(self._storage.edis or {})

    def set_difficulty_tiers(self, difficulty_tiers: Mapping[ProblemId, DifficultyTier]) -> None:
        """Store the tier of each candidate that no stage has dropped.

        The stage calls this before it records its drops.

        Raises:
            ValueError: If the tiers were stored before, or do not cover exactly those candidates.
        """
        self._check_not_written(is_written=self._storage.difficulty_tiers is not None)
        self._check_covers(difficulty_tiers.keys(), self.remaining_problem_ids)
        self._storage.difficulty_tiers = self._restrict_to_remaining(difficulty_tiers)

    def set_core_selection_details(self, core_selection_details: SuiteSelectionDetails) -> None:
        """Store the selection details of the Core, whose suite holds the candidates that no stage has dropped.

        The stage calls this after it records its drops.

        Raises:
            ValueError: If the details were stored before, or the Core does not hold exactly those candidates.
        """
        self._check_not_written(is_written=self._storage.core_selection_details is not None)
        self._check_covers(core_selection_details.benchmark_suite.problem_ids, self.remaining_problem_ids)
        self._storage.core_selection_details = core_selection_details


# ==================================================================================================
#  DistillationStateAccessor
# ==================================================================================================
class DistillationStateAccessor(SelectionStateAccessor):
    """`DistillationStateAccessor` takes the selection details of the suites distilled from the Core.

    The candidates that no stage has dropped are the Core's.
    """

    stage_id = PipelineStageId.DISTILLATION

    def set_distilled_suite_selection_details(
        self, distilled_suite_selection_details: Mapping[str, SuiteSelectionDetails]
    ) -> None:
        """Store the selection details of each distilled suite, keyed by the suite's name.

        The mapping lists the a-series' suites before the b-series', and within each series the suites from largest to
        smallest. Together they hold the candidates that no stage has dropped: the Core.

        Raises:
            ValueError: If the details were stored before, or the suites together do not hold exactly the Core.
        """
        self._check_not_written(is_written=self._storage.distilled_suite_selection_details is not None)
        self._check_covers(
            {
                problem_id
                for details in distilled_suite_selection_details.values()
                for problem_id in details.benchmark_suite.problem_ids
            },
            self.remaining_problem_ids,
        )
        self._storage.distilled_suite_selection_details = dict(distilled_suite_selection_details)
