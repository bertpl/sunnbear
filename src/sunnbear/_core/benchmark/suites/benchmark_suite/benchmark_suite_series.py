"""`BenchmarkSuiteSeries` declares a series of benchmark suites, 1 suite per size, and creates each of its suites."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from sunnbear._core.problems.core import ProblemId

from .benchmark_suite import BenchmarkSuite


# ==================================================================================================
#  BenchmarkSuiteSeries
# ==================================================================================================
@dataclass(frozen=True)
class BenchmarkSuiteSeries:
    """A `BenchmarkSuiteSeries` declares a series of benchmark suites: its sizes, and the name and aliases per size.

    A series holds at most 1 suite per size. It names its suites and gives them its `series_id`. The suite selection
    stage decides how the suites are selected, such as whether a suite holds the series' smaller suites.

    Attributes:
        series_id: The series' id, unique among the series, such as ``sb-a``.
        readable_name: The series' short name for a reader, such as "a-series". The name need not explain the series:
            `summary` explains the series.
        summary: One sentence that tells a reader what the series is for.
        name_format: The format of each suite's name, such as ``sb-{size}a``; its only field, ``{size}``, holds the
            suite's size.
        sizes: The size of each of the series' suites, each a power of 2.
        aliases_by_size: The aliases of each suite that has any, keyed by the suite's size, such as
            ``{64: ("sb-tiny",)}``.
    """

    series_id: str
    readable_name: str
    summary: str
    name_format: str
    sizes: tuple[int, ...]
    aliases_by_size: Mapping[int, tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Refuse an invalid declaration of the series.

        Raises:
            ValueError: If the declaration has any of these defects:

                - `name_format` has no field ``{size}``;
                - a size is not a power of 2, or is declared twice;
                - `aliases_by_size` holds a size that `sizes` does not declare.
        """
        non_power_of_2_sizes = [size for size in self.sizes if size < 1 or size & (size - 1) != 0]
        undeclared_alias_sizes = sorted(set(self.aliases_by_size) - set(self.sizes))
        if "{size}" not in self.name_format:
            raise ValueError(f"The name format {self.name_format!r} of series {self.series_id} has no field {{size}}.")
        elif non_power_of_2_sizes:
            raise ValueError(f"Every size of series {self.series_id} must be a power of 2; it declares {self.sizes}.")
        elif len(set(self.sizes)) != len(self.sizes):
            raise ValueError(f"Series {self.series_id} declares a size twice: {self.sizes}.")
        elif undeclared_alias_sizes:
            raise ValueError(
                f"Series {self.series_id} gives aliases to sizes that it does not declare: {undeclared_alias_sizes}."
            )

    def create_suite(self, problem_ids: Sequence[ProblemId]) -> BenchmarkSuite:
        """Return the series' suite of `problem_ids`, with the name and the aliases of its size.

        Raises:
            ValueError: If the number of `problem_ids` is not 1 of the series' sizes.
        """
        size = len(problem_ids)
        if size not in self.sizes:
            raise ValueError(
                f"Series {self.series_id} has no suite of {size} test problems; its sizes are {self.sizes}."
            )
        else:
            return BenchmarkSuite(
                series_id=self.series_id,
                name=self.name_format.format(size=size),
                aliases=self.aliases_by_size.get(size, ()),
                problem_ids=tuple(problem_ids),
            )
