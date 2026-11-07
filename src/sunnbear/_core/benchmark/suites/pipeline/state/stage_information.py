"""The value objects of this module carry each pipeline stage's information to and from the stage's state accessor.

Each stage's state accessor takes and gives the stage's information in these objects and in plain mappings keyed by
`ProblemId`; a stage whose information has a type of its own in another package, such as `CRange`, `DifficultyClass`
or `CoreComposition`, uses that type.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cached_property
from typing import Any, NamedTuple, Self

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    DiversityFeatureFactory,
    FeatureBlockScales,
    FeatureFidelity,
    FeatureMatrix,
)
from sunnbear._core.benchmark.suites.pipeline.selection import SuiteFamily
from sunnbear._core.problems.core import ProblemId

# In a characterization's table of raw features, each config's column of incorrect solves is named with this prefix and
# the config's solver id.
_N_INCORRECT_SOLVES_PREFIX = "n_incorrect_solves_"


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
        fidelity: The `FeatureFidelity` of the stage's solves and analyses.
        raw_feature_matrix: The raw features of each kept candidate.
        n_incorrect_solves_per_config: For each kept candidate, 1 count per core solver config, in the order of
            `DiversityFeatureFactory.solver_ids`: the number of that config's solves that gave no correct answer.
            Each config solves each candidate `fidelity.solver_mc_size` times.
    """

    fidelity: FeatureFidelity
    raw_feature_matrix: FeatureMatrix
    n_incorrect_solves_per_config: Mapping[ProblemId, tuple[int, ...]]

    @cached_property
    def block_scales(self) -> FeatureBlockScales | None:
        """Return the scale of each block over the kept candidates; ``None`` when the stage keeps fewer than 2."""
        return DiversityFeatureFactory().fit_block_scales(self.raw_feature_matrix)

    def build_scaled_feature_matrix(self, problem_ids: Sequence[ProblemId]) -> FeatureMatrix | None:
        """Return the scaled features of the candidates `problem_ids`; ``None`` when the stage has no block scales."""
        if self.block_scales is None:
            return None
        else:
            return DiversityFeatureFactory().build_scaled_matrix(
                self.raw_feature_matrix.subset(problem_ids), self.block_scales
            )

    def to_raw_features_columns(self) -> dict[str, list[Any]]:
        """Return the results as table columns.

        The columns are ``problem_id``, 1 per feature, and 1 per config with its counts of incorrect solves.
        """
        factory = DiversityFeatureFactory()
        columns: dict[str, list[Any]] = {"problem_id": list(map(str, self.raw_feature_matrix.problem_ids))}
        for name, values in zip(factory.feature_names, self.raw_feature_matrix.values.T, strict=True):
            columns[name] = values.tolist()
        for config_idx, solver_id in enumerate(factory.solver_ids):
            columns[f"{_N_INCORRECT_SOLVES_PREFIX}{solver_id}"] = [
                self.n_incorrect_solves_per_config[problem_id][config_idx]
                for problem_id in self.raw_feature_matrix.problem_ids
            ]
        return columns

    def incorrect_solves_table(self) -> pl.DataFrame:
        """Return, per core solver config, the number and fraction of incorrect solves over the kept candidates.

        The columns are ``solver_id``, ``n_solves``, ``n_incorrect_solves`` and ``incorrect_fraction``, which is null
        when the stage kept no candidate; the rows follow the order of `DiversityFeatureFactory.solver_ids`.
        """
        solver_ids = DiversityFeatureFactory().solver_ids
        n_incorrect_solves = [
            sum(counts[config_idx] for counts in self.n_incorrect_solves_per_config.values())
            for config_idx in range(len(solver_ids))
        ]
        n_solves = len(self.raw_feature_matrix.problem_ids) * self.fidelity.solver_mc_size
        return pl.DataFrame(
            {
                "solver_id": list(solver_ids),
                "n_solves": [n_solves] * len(solver_ids),
                "n_incorrect_solves": n_incorrect_solves,
            },
            schema={"solver_id": pl.String(), "n_solves": pl.Int64(), "n_incorrect_solves": pl.Int64()},
        ).with_columns(
            incorrect_fraction=pl.when(pl.col("n_solves") > 0).then(pl.col("n_incorrect_solves") / pl.col("n_solves"))
        )

    def to_json_values(self) -> dict[str, Any]:
        """Return the parts of the results that `to_raw_features_columns` leaves out, as JSON values."""
        return {"solver_ids": list(DiversityFeatureFactory().solver_ids), "fidelity": self.fidelity.name}

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_raw_features_table(cls, table: pl.DataFrame, json_values: dict[str, Any]) -> Self:
        """Return the results that `table` and `json_values` hold.

        `table` holds the columns of `to_raw_features_columns`, and `json_values` the values of `to_json_values`.

        Raises:
            ValueError: If `json_values` records other solver ids than `DiversityFeatureFactory.solver_ids`, as for
                results that another sunnbear version wrote.
        """
        factory = DiversityFeatureFactory()
        if tuple(json_values["solver_ids"]) != factory.solver_ids:
            raise ValueError(
                f"The results were computed with the solver configs {json_values['solver_ids']}, not with "
                f"{list(factory.solver_ids)}."
            )
        fidelity = FeatureFidelity[json_values["fidelity"]]
        problem_ids = [ProblemId.from_string(problem_id) for problem_id in table["problem_id"]]
        n_incorrect_solves_per_config = table.select(
            f"{_N_INCORRECT_SOLVES_PREFIX}{solver_id}" for solver_id in factory.solver_ids
        ).rows()
        return cls(
            fidelity=fidelity,
            raw_feature_matrix=FeatureMatrix(
                problem_ids=tuple(problem_ids),
                values=table.select(factory.feature_names)
                .to_numpy()
                .reshape(len(problem_ids), len(factory.feature_names)),
            ),
            n_incorrect_solves_per_config=dict(zip(problem_ids, n_incorrect_solves_per_config, strict=True)),
        )


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
