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

    A suite is known by its name and by each of its aliases. The suites that sunnbear builds are:

    - `sb-<size>`, such as `sb-2048`: the Core, from which every other one of these suites is selected;
    - the a-series, `sb-<size>a` from `sb-64a` up to half the Core: the highest-quality selection of benchmark suites;
    - the b-series, `sb-<size>b` of the same sizes: the b-series shares no test problem with the a-series, so it is an
      independent series of benchmark suites, which may be of lower quality.

    Within each series, every suite holds every smaller suite of the series.

    Attributes:
        name: The suite's name, such as ``sb-256a``.
        aliases: The suite's other names, such as ``sb-small``; most suites have none.
        problem_ids: The ids of the suite's test problems.
    """

    name: str
    aliases: tuple[str, ...]
    problem_ids: tuple[ProblemId, ...]

    @property
    def size(self) -> int:
        """Return the number of the suite's test problems."""
        return len(self.problem_ids)

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_json_values(self) -> dict[str, Any]:
        """Return the suite as JSON values: its ``name``, its ``aliases`` and its ``problem_ids`` as strings."""
        return {"name": self.name, "aliases": list(self.aliases), "problem_ids": list(map(str, self.problem_ids))}

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_json_values(cls, json_values: dict[str, Any]) -> Self:
        """Return the suite that the output of `to_json_values` holds."""
        return cls(
            name=json_values["name"],
            aliases=tuple(json_values["aliases"]),
            problem_ids=tuple(map(ProblemId.from_string, json_values["problem_ids"])),
        )
