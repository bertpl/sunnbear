"""`SeriesSelectionSpec` holds what differs between the selections of the series of benchmark suites."""

from dataclasses import dataclass

from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuiteSeries
from sunnbear._core.benchmark.suites.pipeline.selection import CandidateGroup, CandidatePool, ShareQuota


# ==================================================================================================
#  SeriesSelectionSpec
# ==================================================================================================
@dataclass(frozen=True)
class SeriesSelectionSpec:
    """A `SeriesSelectionSpec` holds the candidates and the quotas of the selections of 1 series of benchmark suites.

    `SuiteSelectionStage` selects every suite of the series from the members of `candidate_group`, under `quotas`. How
    the series' suites relate to each other and to the suites of other series is the stage's concern.

    Attributes:
        series: The series whose suites the spec describes.
        candidate_group: The group whose members every suite of the series holds; None for every candidate.
        quotas: The quotas of every suite of the series; empty for a series without quotas.
    """

    series: BenchmarkSuiteSeries
    candidate_group: CandidateGroup | None = None
    quotas: tuple[ShareQuota, ...] = ()

    def restrict_pool(self, candidate_pool: CandidatePool) -> CandidatePool:
        """Return the candidates of `candidate_pool` that `candidate_group` holds, or all of them without a group."""
        if self.candidate_group is None:
            return candidate_pool
        else:
            return candidate_pool.subset(self.candidate_group.member_ids(candidate_pool))
