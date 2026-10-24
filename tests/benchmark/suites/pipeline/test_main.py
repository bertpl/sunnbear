"""``python -m sunnbear._core.benchmark.suites.pipeline`` runs the pipeline over the shipped formulas into the
``--workspace`` directory, and refuses to run without one."""

import runpy
import sys

import pytest

from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGenerationStage, CandidateValidationStage

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
    """The command writes every stage's output into the workspace and prints 1 line per stage, in run order."""
    # --- act --------------------------
    _run_pipeline_command(monkeypatch, ["--workspace", str(tmp_path)])

    # --- assert -----------------------
    printed_output_names = [line.split(":")[0] for line in capsys.readouterr().out.splitlines()]
    assert printed_output_names == _OUTPUT_NAMES
    assert sorted(path.name for path in tmp_path.glob("*.parquet")) == [f"{name}.parquet" for name in _OUTPUT_NAMES]


def test_the_command_requires_a_workspace(monkeypatch, capsys):
    """Without ``--workspace``, the command exits with argparse's usage error, which names the missing option."""
    # --- act --------------------------
    with pytest.raises(SystemExit) as exc_info:
        _run_pipeline_command(monkeypatch, [])

    # --- assert -----------------------
    assert exc_info.value.code == 2
    assert "--workspace" in capsys.readouterr().err
