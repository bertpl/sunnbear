"""`BenchmarkSuite` is a named selection of test problems to benchmark solvers on."""

from dataclasses import dataclass
from typing import Any, Self

from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  BenchmarkSuite
# ==================================================================================================
@dataclass(frozen=True)
class BenchmarkSuite:
    """A `BenchmarkSuite` is a named selection of test problems to benchmark solvers on.

    A suite belongs to 1 `BenchmarkSuiteSeries`, which builds it and gives it its name and aliases; `BUILT_IN_SERIES`
    lists the series that sunnbear builds. A suite is known by its name and by each of its aliases. It stores them, so
    that a suite read back from a file needs no lookup of its series.

    Attributes:
        series_id: The `series_id` of the suite's series, such as ``sb-a``.
        name: The suite's name, such as ``sb-256a``.
        aliases: The suite's other names, such as ``sb-small``; most suites have none.
        problem_ids: The ids of the suite's test problems.
    """

    series_id: str
    name: str
    aliases: tuple[str, ...]
    problem_ids: tuple[ProblemId, ...]

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_json_values(self) -> dict[str, Any]:
        """Return the suite as JSON values: its ``series_id``, ``name``, ``aliases`` and ``problem_ids`` as strings."""
        return {
            "series_id": self.series_id,
            "name": self.name,
            "aliases": list(self.aliases),
            "problem_ids": list(map(str, self.problem_ids)),
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_json_values(cls, json_values: dict[str, Any]) -> Self:
        """Return the suite that the output of `to_json_values` holds."""
        return cls(
            series_id=json_values["series_id"],
            name=json_values["name"],
            aliases=tuple(json_values["aliases"]),
            problem_ids=tuple(map(ProblemId.from_string, json_values["problem_ids"])),
        )
