"""`PipelineStateStorage` holds the candidate registry and every stage's information of 1 pipeline run.

The storage writes its contents into a directory, and reads them back, as `PipelineStateStorage.write_files` describes.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

import polars as pl

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.features import FeatureFidelity, FeatureMatrix, FeatureVectorDefinition
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CoreComposition,
    DifficultyClass,
    DifficultyQuota,
    SuiteFamily,
)
from sunnbear._core.problems.core import ProblemId

from .candidate_registry import CandidateDrop, CandidateRegistry
from .stage_information import (
    CharacterizationResults,
    DistilledSuiteSummary,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)

_TABLE_FILE_SUFFIX = ".parquet"
# This file holds the parts of the storage that are not tables: each characterization's definition and fidelity, the
# Core's composition, and the summaries of the distilled suites.
_STORAGE_FILE_NAME = "storage.json"
# A characterization's table of raw features names each count of incorrect solves after its config, with this prefix.
_N_INCORRECT_SOLVES_PREFIX = "n_incorrect_solves_"


# ==================================================================================================
#  PipelineStateStorage
# ==================================================================================================
@dataclass
class PipelineStateStorage:
    """`PipelineStateStorage` holds the registry of a run's candidates, and 1 structure per stage for its information.

    Only the state accessors write the storage. Each attribute below that holds information on candidates names those
    candidates; a stage's structure is ``None``, or missing from `characterization_results`, until its stage writes the
    structure.

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

    def missing_information(self, stage_id: PipelineStageId) -> list[str]:
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
    def write_files(self, directory: Path) -> None:
        """Write the storage's contents into `directory`, which must exist.

        Each structure that holds information on candidates is 1 Parquet table, named after the structure, with 1 row
        per candidate and the candidate's id in the column ``problem_id``; each characterization's results are the
        table ``<stage id>_raw_features``, with 1 column per feature and 1 count of incorrect solves per config. A
        structure that its stage has not written has no file. The other structures are in 1 JSON file.
        """
        registry = self.candidate_registry
        drops = [registry.drop_of(problem_id) for problem_id in registry.problem_ids]
        self._write_table(
            directory / "candidate_registry",
            {
                "problem_id": list(map(str, registry.problem_ids)),
                "dropped_by": [drop.stage_id.value if drop is not None else None for drop in drops],
                "drop_reason": [drop.reason if drop is not None else None for drop in drops],
                "is_rejection": [drop.is_rejection if drop is not None else None for drop in drops],
            },
        )
        if self.interval_bounds is not None:
            self._write_table(directory / "interval_bounds", self._table_of(self.interval_bounds, "a", "b"))
        if self.c_ranges is not None:
            self._write_table(directory / "c_ranges", self._table_of(self.c_ranges, "c_min", "c_max"))
        for stage_id, results in self.characterization_results.items():
            columns: dict[str, list[Any]] = {"problem_id": list(map(str, results.raw_feature_matrix.problem_ids))}
            for name, values in zip(results.definition.feature_names, results.raw_feature_matrix.values.T, strict=True):
                columns[name] = values.tolist()
            for config_idx, solver_id in enumerate(results.definition.solver_ids):
                columns[f"{_N_INCORRECT_SOLVES_PREFIX}{solver_id}"] = [
                    results.n_incorrect_solves_per_config[problem_id][config_idx]
                    for problem_id in results.raw_feature_matrix.problem_ids
                ]
            self._write_table(directory / f"{stage_id}_raw_features", columns)
        if self.nearest_kept_candidates is not None:
            self._write_table(
                directory / "nearest_kept_candidates",
                {
                    "problem_id": list(map(str, self.nearest_kept_candidates)),
                    "nearest_kept_problem_id": [str(n.problem_id) for n in self.nearest_kept_candidates.values()],
                    "distance": [n.distance for n in self.nearest_kept_candidates.values()],
                },
            )
        if self.edis is not None:
            self._write_table(
                directory / "edis", {"problem_id": list(map(str, self.edis)), "edi": list(self.edis.values())}
            )
        if self.difficulty_classes is not None:
            self._write_table(
                directory / "difficulty_classes",
                {
                    "problem_id": list(map(str, self.difficulty_classes)),
                    "difficulty_class": [c.value for c in self.difficulty_classes.values()],
                },
            )
        if self.suite_memberships is not None:
            self._write_table(
                directory / "suite_memberships",
                {
                    "problem_id": list(map(str, self.suite_memberships)),
                    "suite_family": [m.suite_family.value for m in self.suite_memberships.values()],
                    "smallest_containing_suite_size": [
                        m.smallest_containing_suite_size for m in self.suite_memberships.values()
                    ],
                },
            )
        (directory / _STORAGE_FILE_NAME).write_text(json.dumps(self._json_contents(), indent=2, sort_keys=True) + "\n")

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _table_of(information: dict[ProblemId, Any], *field_names: str) -> dict[str, list[Any]]:
        """Return the table of `information`, with 1 column per field of `field_names` of its values."""
        return {
            "problem_id": list(map(str, information)),
            **{name: [getattr(value, name) for value in information.values()] for name in field_names},
        }

    @staticmethod
    def _write_table(file_stem: Path, columns: dict[str, list[Any]]) -> None:
        """Write `columns` as a Parquet table to `file_stem` with the table suffix."""
        pl.DataFrame(columns).write_parquet(file_stem.with_name(file_stem.name + _TABLE_FILE_SUFFIX))

    def _json_contents(self) -> dict[str, Any]:
        """Return the structures that are not tables, as JSON values."""
        return {
            "characterizations": {
                stage_id.value: {"solver_ids": list(results.definition.solver_ids), "fidelity": results.fidelity.name}
                for stage_id, results in self.characterization_results.items()
            },
            "core_composition": (
                {
                    "quotas": [
                        {"classes": sorted(c.value for c in quota.classes), "count": quota.count}
                        for quota in self.core_composition.quotas
                    ],
                    "class_counts": {c.value: count for c, count in self.core_composition.class_counts.items()},
                }
                if self.core_composition is not None
                else None
            ),
            "distilled_suite_summaries": (
                [
                    {"suite_family": s.suite_family.value, "size": s.size, "diversity": s.diversity}
                    for s in self.distilled_suite_summaries
                ]
                if self.distilled_suite_summaries is not None
                else None
            ),
        }

    @staticmethod
    def _read_table(directory: Path, name: str) -> pl.DataFrame | None:
        """Return the table `name` of `directory`, or ``None`` if it has no such file."""
        file = directory / f"{name}{_TABLE_FILE_SUFFIX}"
        if file.exists():
            return pl.read_parquet(file)
        else:
            return None

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def read_files(cls, directory: Path) -> Self:
        """Return the storage whose contents `write_files` wrote into `directory`."""
        contents = json.loads((directory / _STORAGE_FILE_NAME).read_text())
        storage = cls(candidate_registry=cls._read_candidate_registry(directory))
        for stage_id_value, characterization in contents["characterizations"].items():
            stage_id = PipelineStageId(stage_id_value)
            storage.characterization_results[stage_id] = cls._read_characterization_results(
                directory, stage_id, characterization
            )
        # Each table of 1 row per candidate becomes the structure of the same name, 1 value per row.
        for name, build_value in _VALUE_BUILDERS.items():
            table = cls._read_table(directory, name)
            if table is not None:
                problem_ids = [ProblemId.from_string(problem_id) for problem_id in table["problem_id"]]
                setattr(
                    storage, name, dict(zip(problem_ids, map(build_value, table.iter_rows(named=True)), strict=True))
                )
        if contents["core_composition"] is not None:
            storage.core_composition = CoreComposition(
                quotas=tuple(
                    DifficultyQuota(classes=frozenset(map(DifficultyClass, quota["classes"])), count=quota["count"])
                    for quota in contents["core_composition"]["quotas"]
                ),
                class_counts={
                    DifficultyClass(c): count for c, count in contents["core_composition"]["class_counts"].items()
                },
            )
        if contents["distilled_suite_summaries"] is not None:
            storage.distilled_suite_summaries = tuple(
                DistilledSuiteSummary(
                    suite_family=SuiteFamily(summary["suite_family"]),
                    size=summary["size"],
                    diversity=summary["diversity"],
                )
                for summary in contents["distilled_suite_summaries"]
            )
        return storage

    @classmethod
    def _read_candidate_registry(cls, directory: Path) -> CandidateRegistry:
        """Return the registry that `write_files` wrote into `directory`."""
        table = pl.read_parquet(directory / f"candidate_registry{_TABLE_FILE_SUFFIX}")
        registry = CandidateRegistry()
        registry.add([ProblemId.from_string(problem_id) for problem_id in table["problem_id"]])
        for row in table.filter(pl.col("dropped_by").is_not_null()).iter_rows(named=True):
            registry.record_drop(
                ProblemId.from_string(row["problem_id"]),
                CandidateDrop(
                    stage_id=PipelineStageId(row["dropped_by"]),
                    reason=row["drop_reason"],
                    is_rejection=row["is_rejection"],
                ),
            )
        return registry

    @classmethod
    def _read_characterization_results(
        cls, directory: Path, stage_id: PipelineStageId, characterization: dict[str, Any]
    ) -> CharacterizationResults:
        """Return the results of the characterization stage `stage_id`, from its table and its JSON values."""
        definition = FeatureVectorDefinition(solver_ids=tuple(characterization["solver_ids"]))
        table = pl.read_parquet(directory / f"{stage_id}_raw_features{_TABLE_FILE_SUFFIX}")
        problem_ids = [ProblemId.from_string(problem_id) for problem_id in table["problem_id"]]
        n_incorrect_solves_per_config = table.select(
            f"{_N_INCORRECT_SOLVES_PREFIX}{solver_id}" for solver_id in definition.solver_ids
        ).rows()
        return CharacterizationResults(
            definition=definition,
            fidelity=FeatureFidelity[characterization["fidelity"]],
            raw_feature_matrix=FeatureMatrix(
                problem_ids=tuple(problem_ids),
                values=table.select(definition.feature_names)
                .to_numpy()
                .reshape(len(problem_ids), len(definition.feature_names)),
            ),
            n_incorrect_solves_per_config=dict(zip(problem_ids, n_incorrect_solves_per_config, strict=True)),
        )


# Each structure of 1 value per candidate, other than the characterizations' results, is written as the table of its
# name; each of these functions builds 1 value of the structure from 1 row of the table.
_VALUE_BUILDERS: dict[str, Callable[[dict[str, Any]], object]] = {
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
