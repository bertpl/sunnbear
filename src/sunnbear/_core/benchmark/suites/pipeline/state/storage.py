"""`PipelineStateStorage` holds the candidate registry and every stage's information of 1 pipeline run.

The storage converts its contents to files and back, as `PipelineStateStorage.to_files` describes.
"""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Self

import polars as pl

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CoreComposition,
    DifficultyClass,
    DifficultyQuota,
    SuiteFamily,
)
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.parquet import parquet_file_content

from .candidate_registry import CandidateRegistry
from .stage_information import (
    CharacterizationResults,
    DistilledSuiteSummary,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)

_TABLE_FILE_SUFFIX = ".parquet"
# This file holds the parts of the storage that are not tables, as `_json_contents` returns them.
_JSON_FILE_NAME = "storage.json"


# ==================================================================================================
#  PipelineStateStorage
# ==================================================================================================
@dataclass
class PipelineStateStorage:
    """`PipelineStateStorage` holds the registry of a run's candidates, and 1 structure per stage for its information.

    Only the state accessors write the storage. Each attribute below that holds information on candidates identifies
    those candidates by `ProblemId`; a stage's structure is ``None``, or missing from `characterization_results`, until
    its stage writes the structure.

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

    def unwritten_structure_names(self, stage_id: PipelineStageId) -> list[str]:
        """Return the names of the structures of the stage `stage_id` that the stage has not written yet."""
        is_written_by_name_per_stage: dict[PipelineStageId, dict[str, bool]] = {
            PipelineStageId.CANDIDATE_GENERATION: {"interval_bounds": self.interval_bounds is not None},
            PipelineStageId.CANDIDATE_VALIDATION: {"c_ranges": self.c_ranges is not None},
            PipelineStageId.COARSE_CHARACTERIZATION: {
                "characterization_results": PipelineStageId.COARSE_CHARACTERIZATION in self.characterization_results
            },
            PipelineStageId.SPACING: {"nearest_kept_candidates": self.nearest_kept_candidates is not None},
            PipelineStageId.FULL_CHARACTERIZATION: {
                "characterization_results": PipelineStageId.FULL_CHARACTERIZATION in self.characterization_results,
                "edis": self.edis is not None,
            },
            PipelineStageId.CORE_SELECTION: {
                "difficulty_classes": self.difficulty_classes is not None,
                "core_composition": self.core_composition is not None,
            },
            PipelineStageId.DISTILLATION: {
                "suite_memberships": self.suite_memberships is not None,
                "distilled_suite_summaries": self.distilled_suite_summaries is not None,
            },
        }
        is_written_by_name = is_written_by_name_per_stage[stage_id]
        return [name for name, is_written in is_written_by_name.items() if not is_written]

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_files(self) -> dict[str, bytes]:
        """Return the storage's contents as files, each file name mapped to its content.

        `BenchmarkSuitesBuildDetails.to_files` describes the files, which are all its files except ``run.json``.
        """
        tables = {"candidate_registry": self.candidate_registry.to_columns()}
        if self.interval_bounds is not None:
            tables["interval_bounds"] = self._columns_of(self.interval_bounds, "a", "b")
        if self.c_ranges is not None:
            tables["c_ranges"] = self._columns_of(self.c_ranges, "c_min", "c_max")
        for stage_id, results in self.characterization_results.items():
            tables[f"{stage_id}_raw_features"] = results.to_raw_features_columns()
        if self.nearest_kept_candidates is not None:
            tables["nearest_kept_candidates"] = {
                "problem_id": list(map(str, self.nearest_kept_candidates)),
                "nearest_kept_problem_id": [str(n.problem_id) for n in self.nearest_kept_candidates.values()],
                "distance": [n.distance for n in self.nearest_kept_candidates.values()],
            }
        if self.edis is not None:
            tables["edis"] = {"problem_id": list(map(str, self.edis)), "edi": list(self.edis.values())}
        if self.difficulty_classes is not None:
            tables["difficulty_classes"] = {
                "problem_id": list(map(str, self.difficulty_classes)),
                "difficulty_class": [c.value for c in self.difficulty_classes.values()],
            }
        if self.suite_memberships is not None:
            tables["suite_memberships"] = {
                "problem_id": list(map(str, self.suite_memberships)),
                "suite_family": [m.suite_family.value for m in self.suite_memberships.values()],
                "smallest_containing_suite_size": [
                    m.smallest_containing_suite_size for m in self.suite_memberships.values()
                ],
            }
        files = {f"{name}{_TABLE_FILE_SUFFIX}": parquet_file_content(columns) for name, columns in tables.items()}
        files[_JSON_FILE_NAME] = (json.dumps(self._json_contents(), indent=2, sort_keys=True) + "\n").encode()
        return files

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _columns_of(information: dict[ProblemId, Any], *field_names: str) -> dict[str, list[Any]]:
        """Return `information` as table columns.

        The columns are ``problem_id``, and 1 per name in `field_names` with that field of each value.
        """
        return {
            "problem_id": list(map(str, information)),
            **{name: [getattr(value, name) for value in information.values()] for name in field_names},
        }

    def _json_contents(self) -> dict[str, Any]:
        """Return the structures that are not tables, and each characterization's solver ids and fidelity, as JSON."""
        if self.core_composition is not None:
            core_composition = {
                "quotas": [
                    {"classes": sorted(c.value for c in quota.classes), "count": quota.count}
                    for quota in self.core_composition.quotas
                ],
                "class_counts": {c.value: count for c, count in self.core_composition.class_counts.items()},
            }
        else:
            core_composition = None
        if self.distilled_suite_summaries is not None:
            distilled_suite_summaries = [
                {"suite_family": s.suite_family.value, "size": s.size, "diversity": s.diversity}
                for s in self.distilled_suite_summaries
            ]
        else:
            distilled_suite_summaries = None
        return {
            "characterizations": {
                stage_id.value: results.to_json_values() for stage_id, results in self.characterization_results.items()
            },
            "core_composition": core_composition,
            "distilled_suite_summaries": distilled_suite_summaries,
        }

    @staticmethod
    def _value_builders() -> dict[str, Callable[[dict[str, Any]], object]]:
        """Return the value builder of each structure with 1 value per candidate, except the characterization results.

        Each such structure is written as the table of its name; each value builder builds 1 value of the structure
        from 1 row of that table.
        """
        return {
            "interval_bounds": lambda row: IntervalBounds(a=row["a"], b=row["b"]),
            "c_ranges": lambda row: CRange(c_min=row["c_min"], c_max=row["c_max"]),
            "nearest_kept_candidates": lambda row: NearestKeptCandidate(
                problem_id=ProblemId.from_string(row["nearest_kept_problem_id"]), distance=row["distance"]
            ),
            "edis": lambda row: row["edi"],
            "difficulty_classes": lambda row: DifficultyClass(row["difficulty_class"]),
            "suite_memberships": lambda row: SuiteMembership(
                suite_family=SuiteFamily(row["suite_family"]),
                smallest_containing_suite_size=row["smallest_containing_suite_size"],
            ),
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_files(cls, files: Mapping[str, bytes]) -> Self:
        """Rebuild the storage from the output of `to_files`."""
        json_contents = json.loads(files[_JSON_FILE_NAME])
        storage = cls(
            candidate_registry=CandidateRegistry.from_table(
                pl.read_parquet(files[f"candidate_registry{_TABLE_FILE_SUFFIX}"])
            )
        )
        for stage_id_value, json_values in json_contents["characterizations"].items():
            stage_id = PipelineStageId(stage_id_value)
            storage.characterization_results[stage_id] = CharacterizationResults.from_raw_features_table(
                pl.read_parquet(files[f"{stage_id}_raw_features{_TABLE_FILE_SUFFIX}"]), json_values
            )
        # Each table of 1 row per candidate becomes the structure of the same name, 1 value per row.
        for name, build_value in cls._value_builders().items():
            table_file_name = f"{name}{_TABLE_FILE_SUFFIX}"
            if table_file_name in files:
                table = pl.read_parquet(files[table_file_name])
                problem_ids = [ProblemId.from_string(problem_id) for problem_id in table["problem_id"]]
                setattr(
                    storage, name, dict(zip(problem_ids, map(build_value, table.iter_rows(named=True)), strict=True))
                )
        if json_contents["core_composition"] is not None:
            storage.core_composition = CoreComposition(
                quotas=tuple(
                    DifficultyQuota(classes=frozenset(map(DifficultyClass, quota["classes"])), count=quota["count"])
                    for quota in json_contents["core_composition"]["quotas"]
                ),
                class_counts={
                    DifficultyClass(c): count for c, count in json_contents["core_composition"]["class_counts"].items()
                },
            )
        if json_contents["distilled_suite_summaries"] is not None:
            storage.distilled_suite_summaries = tuple(
                DistilledSuiteSummary(
                    suite_family=SuiteFamily(summary["suite_family"]),
                    size=summary["size"],
                    diversity=summary["diversity"],
                )
                for summary in json_contents["distilled_suite_summaries"]
            )
        return storage
