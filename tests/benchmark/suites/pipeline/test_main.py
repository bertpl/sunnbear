"""``python -m sunnbear._core.benchmark.suites.pipeline`` runs the pipeline over the shipped formulas into the
``--workspace`` directory with ``--n-workers`` workers, prints the rejections per formula, and refuses to run without a
workspace."""

import runpy
import sys

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGenerationStage, CandidateValidationStage
from sunnbear._core.problems.core import FormulaRegistry

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
    # --- arrange ----------------------
    # The command runs over every registered formula. The test keeps 2 families of shipped formulas, because the
    # bisection count check solves 1024 times per valid candidate, which takes about a minute over every formula.
    formulas = tuple(formula for formula in FormulaRegistry.formulas() if formula.number[:3] in {(1, 4, 2), (2, 1, 1)})
    monkeypatch.setattr(FormulaRegistry, "formulas", lambda: formulas)

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
