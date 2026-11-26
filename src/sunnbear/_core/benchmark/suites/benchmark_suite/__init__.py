"""This package holds `BenchmarkSuite`, a named selection of test problems, and the series that build such suites.

- `BenchmarkSuite` is a named selection of test problems to benchmark solvers on;
- `BenchmarkSuiteSeries` declares a series of suites, 1 per size, and builds each of its suites;
- `built_in_series` declares the series that sunnbear builds, and lists them as `BUILT_IN_SERIES`.
"""

from .benchmark_suite import BenchmarkSuite
from .benchmark_suite_series import BenchmarkSuiteSeries
from .built_in_series import BUILT_IN_SERIES, BUILT_IN_SERIES_BY_ID, SB_A_SERIES, SB_B_SERIES
