"""Run the benchmark suite pipeline over the shipped formulas, into the workspace directory given by ``--workspace``.

From the repository root, maintainers run it into a folder under `script_outputs/`::

    uv run python -m sunnbear._core.benchmark.suites.pipeline --workspace script_outputs/pipeline

The workspace has no default directory, because the shipped package cannot assume that the repository's folders
exist. ``--n-workers`` sets the number of worker processes that the stages share.

After the run, the command prints 1 line per stage, then the number of formulas with rejected candidates, and 1 line
per such formula.
"""

import argparse
from pathlib import Path

from sunnbear._core.functions.core import FormulaRegistry

from .core import PipelineWorkspace
from .runner import run_pipeline
from .stages import REJECTIONS_PER_FORMULA_REPORT_NAME, CandidateValidationStage


def main() -> None:
    """Parse the command line, run the pipeline, and print 1 line per stage and the rejections per formula."""
    parser = argparse.ArgumentParser(
        prog="python -m sunnbear._core.benchmark.suites.pipeline",
        description="Run the benchmark suite pipeline over the shipped formulas.",
    )
    parser.add_argument("--workspace", type=Path, required=True, help="directory for the outputs of the stages")
    parser.add_argument("--n-workers", type=int, help="number of worker processes (default: 1 per logical CPU)")
    args = parser.parse_args()

    manifests = run_pipeline(
        workspace_dir=args.workspace, formulas=FormulaRegistry.formulas(), n_workers=args.n_workers
    )
    for manifest in manifests:
        report_names = ", ".join(manifest.report_sha256s) or "none"
        rows = f"{manifest.n_rows} rows, {manifest.n_dropped_rows} dropped"
        print(f"{manifest.output_name}: {rows}, in {manifest.duration_sec:.2f} s; reports: {report_names}")
    rejections_per_formula = PipelineWorkspace(args.workspace).read_report(
        CandidateValidationStage.output_name, REJECTIONS_PER_FORMULA_REPORT_NAME
    )
    for line in CandidateValidationStage.summarize_rejections_per_formula(rejections_per_formula):
        print(line)


if __name__ == "__main__":
    main()
