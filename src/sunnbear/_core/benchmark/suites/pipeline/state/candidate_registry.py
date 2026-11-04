"""`CandidateRegistry` holds every candidate of a pipeline run, by `ProblemId`, with the drop of each dropped one."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Self

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  CandidateRegistry
# ==================================================================================================
class CandidateRegistry:
    """A `CandidateRegistry` holds every candidate of a run, in the order in which it was added, and its drop.

    A dropped candidate keeps its entry, so the registry tells for every candidate which stage dropped it and why.
    """

    def __init__(self) -> None:
        """Create a registry without candidates."""
        self._drop_by_problem_id: dict[ProblemId, CandidateDrop | None] = {}

    @property
    def problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of every candidate, dropped or not, in the order in which they were added."""
        return tuple(self._drop_by_problem_id)

    @property
    def remaining_problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the ids of the candidates that no stage has dropped, in the order in which they were added."""
        return tuple(problem_id for problem_id, drop in self._drop_by_problem_id.items() if drop is None)

    def drop_of(self, problem_id: ProblemId) -> "CandidateDrop | None":
        """Return the drop of the candidate `problem_id`, or ``None`` if no stage has dropped it.

        Raises:
            KeyError: If `problem_id` is not a candidate of the registry.
        """
        return self._drop_by_problem_id[problem_id]

    def problem_ids_dropped_by(self, stage_id: PipelineStageId) -> tuple[ProblemId, ...]:
        """Return the ids of the candidates that the stage `stage_id` dropped, in the order in which they were added."""
        return tuple(
            problem_id
            for problem_id, drop in self._drop_by_problem_id.items()
            if drop is not None and drop.stage_id == stage_id
        )

    def add(self, problem_ids: Sequence[ProblemId]) -> None:
        """Add the candidates `problem_ids`, in their order.

        Raises:
            ValueError: If an id appears twice in `problem_ids`, or is already a candidate of the registry.
        """
        if len(set(problem_ids)) != len(problem_ids) or any(pid in self._drop_by_problem_id for pid in problem_ids):
            raise ValueError("A registry holds each candidate once.")
        else:
            self._drop_by_problem_id.update(dict.fromkeys(problem_ids))

    def record_drop(self, problem_id: ProblemId, drop: "CandidateDrop") -> None:
        """Record that a stage dropped the candidate `problem_id`.

        Raises:
            ValueError: If `problem_id` is not a candidate of the registry, or a stage has dropped it already.
        """
        if problem_id not in self._drop_by_problem_id:
            raise ValueError(f"{problem_id} is not a candidate of the registry.")
        elif self._drop_by_problem_id[problem_id] is not None:
            raise ValueError(f"{problem_id} is a candidate that a stage has dropped already.")
        else:
            self._drop_by_problem_id[problem_id] = drop

    def to_columns(self) -> dict[str, list[Any]]:
        """Return the registry as columns: ``problem_id``, ``drop_stage_id``, ``drop_reason`` and ``is_rejection``.

        The 3 columns of the drop are null for a candidate that no stage has dropped.
        """
        drops = [self.drop_of(problem_id) for problem_id in self.problem_ids]
        return {
            "problem_id": list(map(str, self.problem_ids)),
            "drop_stage_id": [drop.stage_id.value if drop is not None else None for drop in drops],
            "drop_reason": [drop.reason if drop is not None else None for drop in drops],
            "is_rejection": [drop.is_rejection if drop is not None else None for drop in drops],
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_table(cls, table: pl.DataFrame) -> Self:
        """Return the registry whose columns `to_columns` gave, read back from `table`."""
        registry = cls()
        registry.add([ProblemId.from_string(problem_id) for problem_id in table["problem_id"]])
        for row in table.filter(pl.col("drop_stage_id").is_not_null()).iter_rows(named=True):
            registry.record_drop(
                ProblemId.from_string(row["problem_id"]),
                CandidateDrop(
                    stage_id=PipelineStageId(row["drop_stage_id"]),
                    reason=row["drop_reason"],
                    is_rejection=row["is_rejection"],
                ),
            )
        return registry


# ==================================================================================================
#  CandidateDrop
# ==================================================================================================
@dataclass(frozen=True)
class CandidateDrop:
    """A `CandidateDrop` records which stage dropped a candidate, why, and whether the candidate is invalid.

    Attributes:
        stage_id: The `PipelineStageId` of the stage that dropped the candidate.
        reason: The stage's reason, a plain string such as ``bisection_count_not_exact``.
        is_rejection: Whether the stage rejected the candidate as invalid; ``False`` for a valid candidate that the
            stage does not keep, such as a near duplicate.
    """

    stage_id: PipelineStageId
    reason: str
    is_rejection: bool
