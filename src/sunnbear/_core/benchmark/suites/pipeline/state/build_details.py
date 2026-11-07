"""`BenchmarkSuitesBuildDetails` holds a read-only copy of the outcome of 1 run of the benchmark suite pipeline.

`PipelineState.create_build_details` builds the build details, which hold:

- every candidate;
- what each stage that finished found about each candidate;
- which stage dropped each dropped candidate, and why;
- the stage that stopped the run early, if any, and why.

Each consumer builds what it needs from the read methods, which return:

- each finished stage's information, most of it keyed by `ProblemId`;
- each dropped candidate's `CandidateDrop`: the stage that dropped it, and why;
- tables that count the drops and the incorrect solves, list the rejections per formula, and count each suite's test
  problems per difficulty tier.

The build details convert themselves to files and back, and say whether they still fit the installed sunnbear's test
problems.
"""

import copy
import dataclasses
import json
from collections import Counter
from collections.abc import Mapping
from typing import Self

import polars as pl

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStop
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier
from sunnbear._core.problems.core import FormulaRegistry, ProblemId

from .candidate_registry import CandidateDrop
from .stage_information import CharacterizationResults, IntervalBounds, NearestKeptCandidate, SuiteSelectionDetails
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

    def difficulty_tiers(self) -> dict[ProblemId, DifficultyTier] | None:
        """Return core selection's difficulty tier of each candidate that core selection received.

        Return ``None`` when core selection did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CORE_SELECTION, self._storage.difficulty_tiers)

    def core_selection_details(self) -> SuiteSelectionDetails | None:
        """Return core selection's `SuiteSelectionDetails` of the Core.

        Return ``None`` when core selection did not finish.
        """
        return self._copy_if_finished(PipelineStageId.CORE_SELECTION, self._storage.core_selection_details)

    def distilled_suite_selection_details(self) -> dict[str, SuiteSelectionDetails] | None:
        """Return distillation's `SuiteSelectionDetails` of each suite, keyed by the suite's name.

        The suites list the a-series before the b-series, and within each series the suites from largest to smallest.
        Return ``None`` when distillation did not finish.
        """
        return self._copy_if_finished(PipelineStageId.DISTILLATION, self._storage.distilled_suite_selection_details)

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

    def suite_tier_counts(self) -> pl.DataFrame | None:
        """Return 1 row per selected suite, with its number of test problems per difficulty tier.

        The rows list the Core, then the distilled suites in the order of `distilled_suite_selection_details`; they list
        the Core alone when distillation did not finish. The columns are:

        - ``suite_name`` and ``size``;
        - 1 column ``n_candidates_<tier>`` per `DifficultyTier`, with the tier's value in lower case;
        - ``diversity``, the diversity score of the max-div run that selected the suite, null for a suite that no run
          selects.

        Return ``None`` when core selection did not finish.
        """
        core_selection_details = self.core_selection_details()
        difficulty_tiers = self.difficulty_tiers()
        if core_selection_details is None or difficulty_tiers is None:
            return None
        else:
            all_selection_details = [core_selection_details, *(self.distilled_suite_selection_details() or {}).values()]
            rows = []
            for selection_details in all_selection_details:
                suite = selection_details.benchmark_suite
                tier_counts = Counter(difficulty_tiers[problem_id] for problem_id in suite.problem_ids)
                rows.append(
                    {
                        "suite_name": suite.name,
                        "size": suite.size,
                        **{f"n_candidates_{tier.value.lower()}": tier_counts[tier] for tier in DifficultyTier},
                        "diversity": selection_details.diversity,
                    }
                )
            return pl.DataFrame(rows, schema_overrides={"diversity": pl.Float64()})

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_files(self) -> dict[str, bytes]:
        """Return the build details as files, each file name mapped to its content.

        The files are the format of the artifact `benchmark_suites_build_details`:

        - ``run.json`` holds the ids of the finished stages, and the stage that stopped the run and why, or ``null``
          when no stage stopped it;
        - ``storage.json`` holds the information that is not per candidate: each characterization stage's fidelity and
          solver ids, and the `SuiteSelectionDetails` of the Core and of each distilled suite: the suite's name,
          aliases and test problems, and the quotas and diversity score of the max-div run that selected it;
        - each structure of `PipelineStateStorage` that holds information per candidate is 1 Parquet table, named after
          the structure, with 1 row per candidate that the structure covers and the candidate's id in the column
          ``problem_id``. The table ``candidate_registry`` holds every candidate, with the stage and reason of its drop
          and whether the drop is a rejection, which are null for a candidate that no stage dropped;
        - each characterization stage's results are the Parquet table ``<stage id>_raw_features``, with 1 column per
          name of `DiversityFeatureFactory.feature_names` and 1 column ``n_incorrect_solves_<solver id>`` per core
          solver config.

        A structure that its stage has not written has no file. The files also hold what a stage that stopped the run
        wrote before it stopped; the read methods of build details rebuilt from these files still return ``None`` for
        that stage.
        """
        if self.stop is not None:
            stop = dataclasses.asdict(self.stop)
        else:
            stop = None
        run_contents = {"finished_stage_ids": list(self.finished_stage_ids), "stop": stop}
        return self._storage.to_files() | {
            _RUN_FILE_NAME: (json.dumps(run_contents, indent=2, sort_keys=True) + "\n").encode()
        }

    # --------------------------------------------------------------------------
    #  Staleness
    # --------------------------------------------------------------------------
    def staleness_reasons(self) -> list[str]:
        """Return why the build details no longer fit the installed sunnbear's test problems; empty when they fit.

        The build details fit when their candidates are exactly the candidates of the registered formulas, so that a
        consumer finds each of these candidates, and no other, in `FormulaRegistry`. `from_files` checks the build
        details' other references to the installed sunnbear, such as their core solver configs and stage ids, when it
        reads them back.
        """
        registered_problem_ids = {
            candidate.id for formula in FormulaRegistry.formulas() for candidate in formula.build_all_candidates()
        }
        problem_ids = set(self._storage.candidate_registry.problem_ids)
        unregistered_problem_ids = sorted(map(str, problem_ids - registered_problem_ids))
        missing_problem_ids = sorted(map(str, registered_problem_ids - problem_ids))
        reasons = []
        if unregistered_problem_ids:
            reasons.append(
                f"{len(unregistered_problem_ids)} candidates are not registered, e.g. {unregistered_problem_ids[0]}"
            )
        if missing_problem_ids:
            reasons.append(
                f"{len(missing_problem_ids)} registered candidates are missing, e.g. {missing_problem_ids[0]}"
            )
        return reasons

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
    def from_files(cls, files: Mapping[str, bytes]) -> Self:
        """Rebuild the build details from the output of `to_files`.

        Raises:
            ValueError: If the characterization results record core solver configs other than
                `DiversityFeatureFactory.solver_ids`, or the files hold a stage id or a `DifficultyTier` value that
                this sunnbear does not define.
            KeyError: If `files` lacks a file or a field of the `to_files` output.
        """
        run_contents = json.loads(files[_RUN_FILE_NAME])
        if run_contents["stop"] is not None:
            stop = PipelineStop(
                stage_id=PipelineStageId(run_contents["stop"]["stage_id"]), reason=run_contents["stop"]["reason"]
            )
        else:
            stop = None
        return cls(
            storage=PipelineStateStorage.from_files(files),
            finished_stage_ids=tuple(PipelineStageId(stage_id) for stage_id in run_contents["finished_stage_ids"]),
            stop=stop,
        )
