"""``python -m sunnbear._core.benchmark.suites.pipeline`` runs the pipeline over the shipped formulas into the
``--workspace`` directory with ``--n-workers`` workers, prints the rejections per formula, and refuses to run without a
workspace."""

import runpy
import sys

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.__main__ import _print_rejections_per_formula
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    RejectionReason,
)
from sunnbear._core.functions.core import FormulaRegistry

_PIPELINE_PACKAGE = "sunnbear._core.benchmark.suites.pipeline"
_OUTPUT_NAMES = [CandidateGenerationStage.output_name, CandidateValidationStage.output_name]


def _run_pipeline_command(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
    """Run the pipeline package as ``python -m`` runs it, with `args` as its command-line arguments.

    A test that imports every sunnbear module may have imported the package's `__main__` module in this process;
    that module is removed from `sys.modules` first, because `runpy` warns when it finds the module there.
    """
    monkeypatch.setattr(sys, "argv", ["pipeline", *args])
    monkeypatch.delitem(sys.modules, f"{_PIPELINE_PACKAGE}.__main__", raising=False)
    runpy.run_module(_PIPELINE_PACKAGE, run_name="__main__")


def test_the_command_runs_every_stage_into_the_given_workspace(tmp_path, monkeypatch, capsys):
    """The command writes every stage's output into the workspace with the given number of workers, and prints 1 line
    per stage, in run order, then the count of the formulas with rejected candidates."""
    # --- act --------------------------
    _run_pipeline_command(monkeypatch, ["--workspace", str(tmp_path), "--n-workers", "3"])

    # --- assert -----------------------
    printed_lines = capsys.readouterr().out.splitlines()
    assert [line.split(":")[0] for line in printed_lines[: len(_OUTPUT_NAMES)]] == _OUTPUT_NAMES
    n_formulas_with_rejections = len(printed_lines) - len(_OUTPUT_NAMES) - 1
    assert printed_lines[len(_OUTPUT_NAMES)] == (
        f"formulas with rejected candidates: {n_formulas_with_rejections} of {len(FormulaRegistry.formulas())}"
    )
    assert sorted(path.name for path in tmp_path.glob("*.parquet")) == [f"{name}.parquet" for name in _OUTPUT_NAMES]
    manifests = [
        PipelineStageManifest.model_validate_json((tmp_path / "manifests" / f"{name}.json").read_text())
        for name in _OUTPUT_NAMES
    ]
    assert [manifest.n_workers for manifest in manifests] == [3, 3]


def test_the_command_requires_a_workspace(monkeypatch, capsys):
    """Without ``--workspace``, the command exits with argparse's usage error, which names the missing option."""
    # --- act --------------------------
    with pytest.raises(SystemExit) as exc_info:
        _run_pipeline_command(monkeypatch, [])

    # --- assert -----------------------
    assert exc_info.value.code == 2
    assert "--workspace" in capsys.readouterr().err


def test_the_rejections_per_formula_print_1_line_per_formula_with_rejected_candidates(capsys):
    """Only a formula with a rejected candidate gets a line, which counts the rejections of each reason that rejected
    any."""
    # --- arrange ----------------------
    rejection_counts = {reason.value: [0, 0] for reason in RejectionReason}
    rejection_counts[RejectionReason.BOUND_TO_WIDTH_RATIO.value] = [1, 0]
    rejection_counts[RejectionReason.CALIBRATION_NO_SIGN_CHANGE_AT_0.value] = [2, 0]
    rejections_per_formula = pl.DataFrame(
        {"formula_id": ["f1.1.1.1", "f1.1.1.2"], "n_candidates": [4, 2], "n_valid": [1, 2], **rejection_counts}
    )

    # --- act --------------------------
    _print_rejections_per_formula(rejections_per_formula)

    # --- assert -----------------------
    assert capsys.readouterr().out.splitlines() == [
        "formulas with rejected candidates: 1 of 2",
        "  f1.1.1.1: 1 of 4 candidates valid; bound_to_width_ratio: 1, calibration_no_sign_change_at_0: 2",
    ]
