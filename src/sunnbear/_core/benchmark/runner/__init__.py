"""This package holds the benchmark runner: it runs solvers on test functions and stores the results.

- `run_benchmark` runs 1 `BenchmarkTask` per test function in the worker processes of a
  `BenchmarkWorkerPool`, and writes the results to a run directory; every task shares the run's
  `BenchmarkRunSettings`;
- `BenchmarkRunDir` reads and writes the run directory's files, among them the `BenchmarkRunInfo` that
  records what the results depend on;
- `load_results` reads a finished run back, as a table with the columns of `RESULTS_SCHEMA`.
"""

from .exceptions import BenchmarkRunError
from .results_schema import RESULTS_SCHEMA, flop_count_column_name
from .run_dir import BenchmarkRunDir
from .run_info import BenchmarkRunInfo
from .run_settings import BenchmarkRunSettings
from .runner import load_results, run_benchmark
from .task import BenchmarkTask
from .worker_pool import BenchmarkWorkerPool
