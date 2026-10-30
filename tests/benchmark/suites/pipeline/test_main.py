"""``python -m sunnbear._core.benchmark.suites.pipeline`` runs the pipeline over the shipped formulas into the
``--workspace`` directory with ``--n-workers`` workers, prints the rejections per formula and the stop of a stage that
stops the run, exits normally when no stage stops it, and refuses to run without a workspace."""

import re
import runpy
import sys

import pytest

from sunnbear._core.benchmark.suites.pipeline import runner
from sunnbear._core.benchmark.suites.pipeline.core import PipelineRunResult, PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    CoreSelectionStage,
    FullCharacterizationStage,
    SpacingStage,
)
from sunnbear._core.problems.core import FormulaRegistry

_PIPELINE_PACKAGE = "sunnbear._core.benchmark.suites.pipeline"
_OUTPUT_NAMES = [
    CandidateGenerationStage.output_name,
    CandidateValidationStage.output_name,
    CoarseCharacterizationStage.output_name,
    SpacingStage.output_name,
    FullCharacterizationStage.output_name,
]


def _run_pipeline_command(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
    """Run the pipeline package as ``python -m`` runs it, with `args` as its command-line arguments.

    A test that imports every sunnbear module may have imported the package's `__main__` module in this process;
    that module is removed from `sys.modules` first, because `runpy` warns when it finds the module there.
    """
    monkeypatch.setattr(sys, "argv", ["pipeline", *args])
    monkeypatch.delitem(sys.modules, f"{_PIPELINE_PACKAGE}.__main__", raising=False)
    runpy.run_module(_PIPELINE_PACKAGE, run_name="__main__")


@pytest.mark.only_with_numba_jit
def test_the_command_runs_every_stage_into_the_given_workspace(tmp_path, monkeypatch, capsys):
    """The command writes each stage's output into the workspace with the given number of workers, until core selection
    stops the run, because the test's 3 candidates fill no Core.

    It prints 1 line per stage that wrote its output, in run order, then for each stage that rejects candidates the
    count of the formulas with rejected candidates, followed by 1 indented line per such formula, then the stop, and
    exits with status 1."""
    # --- arrange ----------------------
    # The command runs over every registered formula. The test keeps only the shipped formulas whose numbers start with
    # (1, 4, 2), because validation runs solves at every tuple of the shipped tuple set's largest size for each
    # candidate that passes its earlier checks, and full characterization does the same for each candidate that spacing
    # keeps, which makes a run over every formula slow.
    formulas = tuple(formula for formula in FormulaRegistry.formulas() if formula.number[:3] == (1, 4, 2))
    monkeypatch.setattr(FormulaRegistry, "formulas", lambda: formulas)

    # --- act --------------------------
    with pytest.raises(SystemExit) as exc_info:
        _run_pipeline_command(monkeypatch, ["--workspace", str(tmp_path), "--n-workers", "3"])

    # --- assert -----------------------
    assert exc_info.value.code == 1
    [*printed_lines, stop_line] = capsys.readouterr().out.splitlines()
    assert stop_line.startswith(f"{CoreSelectionStage.output_name}: stopped: The candidates fill no Core of 128")
    assert [line.split(":")[0] for line in printed_lines[: len(_OUTPUT_NAMES)]] == _OUTPUT_NAMES
    count_line_indices = [idx for idx, line in enumerate(printed_lines) if not line.startswith("  ")]
    count_line_indices = count_line_indices[len(_OUTPUT_NAMES) :]
    rejecting_output_names = [
        CandidateValidationStage.output_name,
        CoarseCharacterizationStage.output_name,
        FullCharacterizationStage.output_name,
    ]
    assert [printed_lines[idx].split(":")[0] for idx in count_line_indices] == rejecting_output_names
    for idx, next_idx in zip(count_line_indices, [*count_line_indices[1:], len(printed_lines)], strict=True):
        n_formulas_with_rejections = next_idx - idx - 1
        assert re.fullmatch(
            rf"\w+: formulas with rejected candidates: {n_formulas_with_rejections} of \d+", printed_lines[idx]
        )
    assert sorted(path.name for path in tmp_path.glob("*.parquet")) == [f"{name}.parquet" for name in _OUTPUT_NAMES]
    manifests = [
        PipelineStageManifest.model_validate_json((tmp_path / "manifests" / f"{name}.json").read_text())
        for name in _OUTPUT_NAMES
    ]
    assert [manifest.n_workers for manifest in manifests] == [3] * len(_OUTPUT_NAMES)


def test_the_command_exits_normally_when_no_stage_stops_the_run(tmp_path, monkeypatch, capsys):
    """When every stage writes its output, the command prints no stop and returns without an exit status; the test
    replaces the run by one that wrote no stage, because the shipped formulas take long to fill a Core."""
    # --- arrange ----------------------
    monkeypatch.setattr(runner, "run_pipeline", lambda **_kwargs: PipelineRunResult(manifests=(), stop=None))

    # --- act --------------------------
    _run_pipeline_command(monkeypatch, ["--workspace", str(tmp_path)])

    # --- assert -----------------------
    assert capsys.readouterr().out == ""


def test_the_command_requires_a_workspace(monkeypatch, capsys):
    """Without ``--workspace``, the command exits with argparse's usage error, which names the missing option."""
    # --- act --------------------------
    with pytest.raises(SystemExit) as exc_info:
        _run_pipeline_command(monkeypatch, [])

    # --- assert -----------------------
    assert exc_info.value.code == 2
    assert "--workspace" in capsys.readouterr().err
