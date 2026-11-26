"""This module declares the series of benchmark suites that sunnbear builds, 1 constant per series.

`BUILT_IN_SERIES` lists every such series, in the order in which sunnbear lists their suites, and
`BUILT_IN_SERIES_BY_ID` finds each by its `series_id`. A reader that lists the series or looks up a suite's series goes
through these 2, so that a new series needs no change to the reader.
"""

from .benchmark_suite_series import BenchmarkSuiteSeries

SB_A_SERIES = BenchmarkSuiteSeries(
    series_id="sb-a",
    readable_name="a-series",
    summary="The a-series holds the most diverse test problems that sunnbear selects, to benchmark solvers on.",
    name_format="sb-{size}a",
    sizes=(1024, 512, 256, 128, 64),
    aliases_by_size={
        1024: ("sb-large",),
        512: ("sb-medium",),
        256: ("sb-small",),
        128: ("sb-xsmall",),
        64: ("sb-tiny",),
    },
)
SB_B_SERIES = BenchmarkSuiteSeries(
    series_id="sb-b",
    readable_name="b-series",
    summary=(
        "The b-series is disjoint from the a-series and diversified with respect to it, so that a solver can be "
        "calibrated on its test problems and benchmarked on those of the a-series."
    ),
    name_format="sb-{size}b",
    sizes=(1024, 512, 256, 128, 64),
)

BUILT_IN_SERIES = (SB_A_SERIES, SB_B_SERIES)
BUILT_IN_SERIES_BY_ID = {series.series_id: series for series in BUILT_IN_SERIES}
