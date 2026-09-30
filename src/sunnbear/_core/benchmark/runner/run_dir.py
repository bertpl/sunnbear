"""`BenchmarkRunDir` represents the directory of 1 benchmark run, and is the only code that reads or writes its files.

The directory holds:

- `run_info.json`, the run's `BenchmarkRunInfo`;
- 1 results file per formula, e.g. `f2.1.1.parquet`, which holds the rows of every test function of the
  formula, written once all of them have run;
- `staging/`, which holds 1 results file per finished test function of each formula whose results file is
  not written yet, e.g. `staging/f2.1.1/0.parquet` for the formula's first test function in run order, the
  order in which the formula's test functions run; a formula's staging directory is removed once its results
  file is written, and `staging/` once it is empty.

Every file is written under a temporary name and then renamed, so a crash never leaves a partly written
file under its final name, and a file that exists is complete.
"""

import shutil
from collections.abc import Callable
from pathlib import Path

import polars as pl

from .exceptions import BenchmarkRunError
from .run_info import BenchmarkRunInfo

_RUN_INFO_FILE_NAME = "run_info.json"
_STAGING_DIR_NAME = "staging"
_RESULTS_FILE_SUFFIX = ".parquet"
_TEMPORARY_FILE_SUFFIX = ".tmp"


# ==================================================================================================
#  BenchmarkRunDir
# ==================================================================================================
class BenchmarkRunDir:
    """`BenchmarkRunDir` reads and writes the files of 1 benchmark run's directory."""

    def __init__(self, path: Path) -> None:
        """Refer to the run directory at `path`, which need not exist yet."""
        self.path = path

    # --------------------------------------------------------------------------
    #  Run info
    # --------------------------------------------------------------------------
    def store_or_check_run_info(self, run_info: BenchmarkRunInfo) -> BenchmarkRunInfo:
        """Store `run_info` when the directory holds no run; else check `run_info` against the stored run info.

        The directory is created when it does not exist.

        Returns:
            The run info of the directory's run: `run_info` for a new run, the stored run info for a resumed one.

        Raises:
            BenchmarkRunError: If the stored run info is malformed, or belongs to a run with other inputs or
                versions.
        """
        stored_run_info = self.read_run_info()
        if stored_run_info is None:
            self.write_run_info(run_info)
            return run_info
        else:
            stored_run_info.check_resumable_as(run_info)
            return stored_run_info

    def read_run_info(self) -> BenchmarkRunInfo | None:
        """Return the stored run info, or ``None`` when the directory holds none.

        Raises:
            BenchmarkRunError: If the stored run info is malformed.
        """
        run_info_file = self.path / _RUN_INFO_FILE_NAME
        if run_info_file.is_file():
            return BenchmarkRunInfo.from_json(run_info_file.read_text())
        else:
            return None

    def write_run_info(self, run_info: BenchmarkRunInfo) -> None:
        """Store `run_info`, creating the directory when needed and replacing any stored run info."""
        self.path.mkdir(parents=True, exist_ok=True)
        self._write_atomically(self.path / _RUN_INFO_FILE_NAME, lambda file: file.write_text(run_info.to_json()))

    def mark_finished(self, run_info: BenchmarkRunInfo) -> None:
        """Store `run_info` with `finished_at` set to now, unless the run is already finished."""
        if not run_info.is_finished:
            self.write_run_info(run_info.with_finished_at_now())

    # --------------------------------------------------------------------------
    #  Results
    # --------------------------------------------------------------------------
    def has_formula_results(self, formula_id: str) -> bool:
        """Return whether the results file of the formula `formula_id`, e.g. ``f2.1.1``, was written."""
        return self._formula_results_file(formula_id).is_file()

    def has_staged_function_results(self, formula_id: str, function_idx: int) -> bool:
        """Return whether the results of a formula's test function were staged.

        Args:
            formula_id: The formula's id, e.g. ``f2.1.1``.
            function_idx: The position of the test function among the formula's test functions, in run
                order.
        """
        return self._staged_function_results_file(formula_id, function_idx).is_file()

    def stage_function_results(self, formula_id: str, function_idx: int, results: pl.DataFrame) -> None:
        """Store the results of a formula's test function until all of the formula's test functions have run.

        Args:
            formula_id: The formula's id, e.g. ``f2.1.1``.
            function_idx: The position of the test function among the formula's test functions, in run
                order.
            results: The test function's result rows.
        """
        staged_file = self._staged_function_results_file(formula_id, function_idx)
        staged_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_atomically(staged_file, results.write_parquet)

    def write_formula_results(self, formula_id: str, n_functions: int) -> None:
        """Write the formula's results file from its `n_functions` staged results, in run order, then remove them.

        Raises:
            BenchmarkRunError: If the results of a test function of the formula were not staged.
        """
        staged_files = [self._staged_function_results_file(formula_id, idx) for idx in range(n_functions)]
        missing_file_names = [file.name for file in staged_files if not file.is_file()]
        if missing_file_names:
            raise BenchmarkRunError(f"Formula {formula_id} is missing the staged results files {missing_file_names}.")
        results = pl.concat([pl.read_parquet(file) for file in staged_files])
        self._write_atomically(self._formula_results_file(formula_id), results.write_parquet)
        staging_dir = self.path / _STAGING_DIR_NAME
        shutil.rmtree(staging_dir / formula_id)
        if not any(staging_dir.iterdir()):
            staging_dir.rmdir()

    def write_formula_results_if_all_staged(self, formula_id: str, n_functions: int) -> None:
        """Write the formula's results file if the results of all its `n_functions` test functions are staged."""
        if all(self.has_staged_function_results(formula_id, idx) for idx in range(n_functions)):
            self.write_formula_results(formula_id, n_functions)

    def read_finished_run_info(self) -> BenchmarkRunInfo:
        """Return the stored run info of a finished run.

        Raises:
            BenchmarkRunError: If the directory holds no run info, a malformed run info, or a run that is not finished.
        """
        run_info = self.read_run_info()
        if run_info is None:
            raise BenchmarkRunError(f"{self.path} holds no benchmark run.")
        if not run_info.is_finished:
            raise BenchmarkRunError(f"The benchmark run in {self.path} is not finished; resume it first.")
        return run_info

    def scan_results(self) -> pl.LazyFrame:
        """Return a lazy frame over every formula's results file of a finished run.

        Raises:
            BenchmarkRunError: If the directory holds no run info, a malformed run info, or a run that is not finished.
        """
        run_info = self.read_finished_run_info()
        return pl.scan_parquet([self._formula_results_file(formula_id) for formula_id in run_info.formula_ids])

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _formula_results_file(self, formula_id: str) -> Path:
        """Return the path of a formula's results file."""
        return self.path / f"{formula_id}{_RESULTS_FILE_SUFFIX}"

    def _staged_function_results_file(self, formula_id: str, function_idx: int) -> Path:
        """Return the path of the staged results of a formula's test function."""
        return self.path / _STAGING_DIR_NAME / formula_id / f"{function_idx}{_RESULTS_FILE_SUFFIX}"

    @staticmethod
    def _write_atomically(file: Path, write_file: Callable[[Path], object]) -> None:
        """Write `file` with `write_file` under a temporary name, then rename it, so `file` is never partly written."""
        temporary_file = file.with_name(file.name + _TEMPORARY_FILE_SUFFIX)
        write_file(temporary_file)
        temporary_file.replace(file)
