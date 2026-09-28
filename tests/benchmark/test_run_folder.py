"""`BenchmarkRunFolder` writes a formula's results file from its staged results, and only once all are staged."""

import polars as pl
import pytest

from sunnbear._core.benchmark.exceptions import BenchmarkRunError
from sunnbear._core.benchmark.run_folder import BenchmarkRunFolder


def test_a_formula_results_file_needs_the_staged_results_of_every_test_function(tmp_path):
    """Writing a formula's results file raises `BenchmarkRunError` naming each test function without staged results."""
    # --- arrange ----------------------
    run_folder = BenchmarkRunFolder(tmp_path)

    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match=r"f2\.1\.1 has no staged results in \['0.parquet', '1.parquet'\]"):
        run_folder.write_formula_results("f2.1.1", 2)


def test_a_formula_results_file_holds_its_staged_results_in_run_order_and_keeps_other_staging(tmp_path):
    """A formula's results file joins its staged results in run order; other formulas' staged results are kept."""
    # --- arrange ----------------------
    run_folder = BenchmarkRunFolder(tmp_path)
    run_folder.stage_function_results("f2.1.1", 1, pl.DataFrame({"function_idx": [1, 1]}))
    run_folder.stage_function_results("f2.1.1", 0, pl.DataFrame({"function_idx": [0]}))
    run_folder.stage_function_results("f2.1.2", 0, pl.DataFrame({"function_idx": [0]}))

    # --- act --------------------------
    run_folder.write_formula_results("f2.1.1", 2)

    # --- assert -----------------------
    assert pl.read_parquet(tmp_path / "f2.1.1.parquet")["function_idx"].to_list() == [0, 1, 1]
    assert run_folder.has_formula_results("f2.1.1")
    assert not run_folder.has_staged_function_results("f2.1.1", 0)
    assert run_folder.has_staged_function_results("f2.1.2", 0)
