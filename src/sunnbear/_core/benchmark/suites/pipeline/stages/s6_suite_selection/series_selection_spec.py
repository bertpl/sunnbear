"""`SeriesSelectionSpec` holds a series of benchmark suites with its candidate group and its quotas."""

from dataclasses import dataclass

from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuiteSeries
from sunnbear._core.benchmark.suites.pipeline.selection import CandidateGroup, ShareQuota


# ==================================================================================================
#  SeriesSelectionSpec
# ==================================================================================================
@dataclass(frozen=True)
class SeriesSelectionSpec:
    """A `SeriesSelectionSpec` holds a series of benchmark suites, with the candidate group and quotas of its suites.

    Attributes:
        candidate_group: Each suite of the series holds only members of this group; None allows every candidate.
        quotas: The quotas of every suite of the series; empty for a series without quotas.
    """

    series: BenchmarkSuiteSeries
    candidate_group: CandidateGroup | None = None
    quotas: tuple[ShareQuota, ...] = ()
