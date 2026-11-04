"""`BenchmarkSuitesBuildDetails` holds a read-only copy of the outcome of 1 run of the benchmark suite pipeline.

`PipelineState.create_build_details` builds the build details, which hold:

- every candidate;
- what each stage that finished found about each candidate;
- which stage dropped each dropped candidate, and why;
- the stage that stopped the run early, if any, and why.

Each consumer builds what it needs from the read methods, which return:

- each finished stage's information, most of it keyed by `ProblemId`;
- each dropped candidate's `CandidateDrop`: the stage that dropped it, and why;
- tables that count the drops and the incorrect solves, list the rejections per formula, and describe the
  distilled suites.

The build details write their files into a directory, and read them back.
"""

import copy
import dataclasses
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Self

import polars as pl

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStop
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateDrop
from .stage_information import (
    CharacterizationResults,
    DistilledSuiteSummary,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)
from .storage import PipelineStateStorage

_RUN_FILE_NAME = "run.json"


# ==================================================================================================
#  BenchmarkSuitesBuildDetails
# ==================================================================================================
class BenchmarkSuitesBuildDetails:
    """`BenchmarkSuitesBuildDetails` holds every candidate of a run, and the information of each stage that finished.

    The build details are read-only: they copy the run's information when they are created, and each read method
    returns a copy or an immutable value. A stage that stopped the run did not finish, so its information is not part of
    the build details.

    Attributes:
        finished_stage_ids: The stages that ran to their end, in run order.
        stop: The stage that stopped the run, and why; ``None`` when every stage of the run finished.
    """

    def __init__(
        self,
        *,
        storage: PipelineStateStorage,
        finished_stage_ids: tuple[PipelineStageId, ...],
        stop: PipelineStop | None,
    ) -> None:
        """Create the build details of a run whose information `storage` holds, which the build details copy."""
        self._storage = copy.deepcopy(storage)
        self.finished_stage_ids = finished_stage_ids
        self.stop = stop

    # --------------------------------------------------------------------------
    #  Candidates and drops
    # --------------------------------------------------------------------------
    @property
    def problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of every candidate, dropped or not, in the order of candidate generation."""
        return self._storage.candidate_registry.problem_ids

    @property
    def remaining_problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of the candidates that no stage dropped, in the order of candidate generation."""
        return self._storage.candidate_registry.remaining_problem_ids

    def drop_of(self, problem_id: ProblemId) -> CandidateDrop | None:
        """Return the `CandidateDrop` of the candidate `problem_id`, or ``None`` if no stage dropped it.

        Raises:
            KeyError: If `problem_id` is not a candidate of the run.
        """
        return self._storage.candidate_registry.drop_of(problem_id)

    # --------------------------------------------------------------------------
    #  Each finished stage's information, or None for a stage that did not finish
    # --------------------------------------------------------------------------
    def interval_bounds(self) -> dict[ProblemId, IntervalBounds] | None:
        """Return candidate generation's interval bounds of each candidate.

        Return ``None`` when candidate generation did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CANDIDATE_GENERATION, self._storage.interval_bounds)

    def c_ranges(self) -> dict[ProblemId, CRange] | None:
        """Return validation's c-range of each valid candidate.

        Return ``None`` when validation did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CANDIDATE_VALIDATION, self._storage.c_ranges)

    def characterization_results(self, stage_id: PipelineStageId) -> CharacterizationResults | None:
        """Return the results of the characterization stage `stage_id` on the candidates that it kept.

        Return ``None`` for a stage that did not finish.
        """
        return self._copy_if_finished(stage_id, self._storage.characterization_results.get(stage_id))

    def nearest_kept_candidates(self) -> dict[ProblemId, NearestKeptCandidate] | None:
        """Return, for each candidate that the spacing stage dropped, its nearest kept candidate.

        Return ``None`` when spacing did not finish.
        """
        return self._copy_if_finished(PipelineStageId.SPACING, self._storage.nearest_kept_candidates)

    def edis(self) -> dict[ProblemId, float] | None:
        """Return full characterization's empirical difficulty index (EDI) of each candidate that it kept.

        Return ``None`` when full characterization did not finish.
        """
        return self._copy_if_finished(PipelineStageId.FULL_CHARACTERIZATION, self._storage.edis)

    def difficulty_classes(self) -> dict[ProblemId, DifficultyClass] | None:
        """Return core selection's difficulty class of each candidate that core selection received.

        Return ``None`` when core selection did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CORE_SELECTION, self._storage.difficulty_classes)

    def core_composition(self) -> CoreComposition | None:
        """Return core selection's composition of the Core.

        Return ``None`` when core selection did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CORE_SELECTION, self._storage.core_composition)

    def suite_memberships(self) -> dict[ProblemId, SuiteMembership] | None:
        """Return distillation's `SuiteMembership` of each Core member.

        Return ``None`` when distillation did not finish.
        """
        return self._copy_if_finished(PipelineStageId.DISTILLATION, self._storage.suite_memberships)

    def distilled_suite_summaries(self) -> tuple[DistilledSuiteSummary, ...] | None:
        """Return distillation's summary of each suite: benchmark suites first, each family's suites largest first.

        Return ``None`` when distillation did not finish.
        """
        return self._copy_if_finished(PipelineStageId.DISTILLATION, self._storage.distilled_suite_summaries)

    # --------------------------------------------------------------------------
    #  Tables
    # --------------------------------------------------------------------------
    def drop_counts(self) -> pl.DataFrame:
        """Return 1 row per formula, stage and reason of a drop, with the number of candidates dropped.

        The columns are ``formula_id``, ``stage_id``, ``reason``, ``is_rejection`` and ``n_dropped``; the rows follow
        the run order of the stages, and within a stage the order of each formula's first drop.
        """
        counts = Counter(
            (problem_id.formula_id, drop.stage_id, drop.reason, drop.is_rejection)
            for problem_id in self.problem_ids
            if (drop := self.drop_of(problem_id)) is not None
        )
        stage_order = list(PipelineStageId)
        rows = sorted(counts.items(), key=lambda item: stage_order.index(item[0][1]))
        return pl.DataFrame(
            [
                {
                    "formula_id": formula_id,
                    "stage_id": stage_id.value,
                    "reason": reason,
                    "is_rejection": is_rejection,
                    "n_dropped": n_dropped,
                }
                for (formula_id, stage_id, reason, is_rejection), n_dropped in rows
            ],
            schema={
                "formula_id": pl.String(),
                "stage_id": pl.String(),
                "reason": pl.String(),
                "is_rejection": pl.Boolean(),
                "n_dropped": pl.Int64(),
            },
        )

    def candidate_counts(self, stage_id: PipelineStageId) -> pl.DataFrame:
        """Return 1 row per formula whose candidates reached the stage `stage_id`, and how many of them it kept.

        The columns are:

        - ``formula_id``;
        - ``n_candidates``, the number of the formula's candidates that no stage before `stage_id` dropped;
        - ``n_kept``, the number of those candidates that `stage_id` did not drop either.

        The rows follow the order of candidate generation.
        """
        stage_position = list(PipelineStageId).index(stage_id)
        n_candidates: Counter[str] = Counter()
        n_kept: Counter[str] = Counter()
        for problem_id in self.problem_ids:
            drop = self.drop_of(problem_id)
            if drop is not None:
                drop_position = list(PipelineStageId).index(drop.stage_id)
            else:
                drop_position = len(PipelineStageId)
            if drop_position >= stage_position:
                n_candidates[problem_id.formula_id] += 1
                n_kept[problem_id.formula_id] += int(drop_position > stage_position)
        return pl.DataFrame(
            {
                "formula_id": list(n_candidates),
                "n_candidates": list(n_candidates.values()),
                "n_kept": [n_kept[formula_id] for formula_id in n_candidates],
            },
            schema={"formula_id": pl.String(), "n_candidates": pl.Int64(), "n_kept": pl.Int64()},
        )

    def rejections_per_formula(self, stage_id: PipelineStageId) -> list[tuple[str, int, int, dict[str, int]]]:
        """Return the rejections of the stage `stage_id`, per formula with candidates that the stage rejected.

        Each item holds the formula id, the formula's numbers of candidates and of kept candidates, as in
        `candidate_counts`, and its number of rejections per reason. The items follow the order of candidate generation.
        """
        rejections = self.drop_counts().filter((pl.col("stage_id") == stage_id.value) & pl.col("is_rejection"))
        rejected_formula_ids = set(rejections["formula_id"])
        return [
            (
                row["formula_id"],
                row["n_candidates"],
                row["n_kept"],
                dict(rejections.filter(pl.col("formula_id") == row["formula_id"]).select("reason", "n_dropped").rows()),
            )
            for row in self.candidate_counts(stage_id).iter_rows(named=True)
            if row["formula_id"] in rejected_formula_ids
        ]

    def incorrect_solves_table(self, stage_id: PipelineStageId) -> pl.DataFrame | None:
        """Return the number and fraction of incorrect solves of each core solver config of the stage `stage_id`.

        The columns are those of `CharacterizationResults.incorrect_solves_table`. Return ``None`` for a stage that did
        not finish.
        """
        results = self.characterization_results(stage_id)
        if results is None:
            return None
        else:
            return results.incorrect_solves_table()

    def suite_compositions(self) -> pl.DataFrame | None:
        """Return 1 row per distilled suite, in the order of `distilled_suite_summaries`, with its composition.

        The columns are:

        - ``suite_family`` and ``size``;
        - 1 column ``n_candidates_<class>`` per `DifficultyClass`, with the class's value in lower case;
        - ``diversity``.

        Return ``None`` when distillation did not finish.
        """
        summaries = self.distilled_suite_summaries()
        memberships = self.suite_memberships()
        difficulty_classes = self.difficulty_classes()
        if summaries is None or memberships is None or difficulty_classes is None:
            return None
        else:
            rows = []
            for summary in summaries:
                class_counts = Counter(
                    difficulty_classes[problem_id]
                    for problem_id, membership in memberships.items()
                    if membership.suite_family is summary.suite_family
                    and membership.smallest_containing_suite_size <= summary.size
                )
                rows.append(
                    {
                        "suite_family": summary.suite_family.value,
                        "size": summary.size,
                        **{f"n_candidates_{c.value.lower()}": class_counts[c] for c in DifficultyClass},
                        "diversity": summary.diversity,
                    }
                )
            return pl.DataFrame(rows, schema_overrides={"diversity": pl.Float64()})

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def write_files(self, directory: Path) -> None:
        """Write the build details into `directory`, after removing any files that it holds.

        The directory holds, in 1 JSON file, the ids of the finished stages and the stage that stopped the run and why,
        beside the files that `PipelineStateStorage.write_files` writes.

        Those files also hold what a stage that stopped the run wrote before it stopped; the read methods of the build
        details read back from them still return ``None`` for that stage.
        """
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True)
        if self.stop is not None:
            stop = dataclasses.asdict(self.stop)
        else:
            stop = None
        run_contents = {"finished_stage_ids": list(self.finished_stage_ids), "stop": stop}
        (directory / _RUN_FILE_NAME).write_text(json.dumps(run_contents, indent=2, sort_keys=True) + "\n")
        self._storage.write_files(directory)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _copy_if_finished[T](self, stage_id: PipelineStageId, information: T) -> T | None:
        """Return a copy of `information` if the stage `stage_id` finished, else ``None``."""
        if stage_id in self.finished_stage_ids:
            return copy.deepcopy(information)
        else:
            return None

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def read_files(cls, directory: Path) -> Self:
        """Return the build details that `write_files` wrote into `directory`."""
        run_contents = json.loads((directory / _RUN_FILE_NAME).read_text())
        if run_contents["stop"] is not None:
            stop = PipelineStop(
                stage_id=PipelineStageId(run_contents["stop"]["stage_id"]), reason=run_contents["stop"]["reason"]
            )
        else:
            stop = None
        return cls(
            storage=PipelineStateStorage.read_files(directory),
            finished_stage_ids=tuple(PipelineStageId(stage_id) for stage_id in run_contents["finished_stage_ids"]),
            stop=stop,
        )
