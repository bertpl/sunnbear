"""Run the benchmark suite pipeline over the shipped formulas, into the workspace directory given by ``--workspace``.

From the repository root, maintainers run it into a folder under `script_outputs/`::

    uv run python -m sunnbear._core.benchmark.suites.pipeline --workspace script_outputs/pipeline

The workspace has no default directory, because the shipped package cannot assume that the repository's folders
exist. ``--n-workers`` sets the number of worker processes that the stages share.

After the run, it prints 1 line per stage, then 1 line per formula that validation rejected candidates of.
"""

import argparse
from pathlib import Path

import polars as pl

from sunnbear._core.functions.core import FormulaRegistry

from .core import PipelineWorkspace
from .runner import run_pipeline
from .stages import REJECTIONS_PER_FORMULA_REPORT_NAME, CandidateValidationStage, RejectionReason


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
    _print_rejections_per_formula(rejections_per_formula)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _print_rejections_per_formula(rejections_per_formula: pl.DataFrame) -> None:
    """Print a count of the formulas that validation rejected candidates of, then 1 line per such formula.

    A formula's line gives its numbers of valid candidates and of candidates, and the number of rejected candidates
    per `RejectionReason` that rejected any.
    """
    formulas_with_rejections = rejections_per_formula.filter(pl.col("n_valid") < pl.col("n_candidates"))
    print(f"formulas with rejected candidates: {formulas_with_rejections.height} of {rejections_per_formula.height}")
    for row in formulas_with_rejections.iter_rows(named=True):
        rejections = ", ".join(
            f"{reason.value}: {row[reason.value]}" for reason in RejectionReason if row[reason.value] > 0
        )
        print(f"  {row['formula_id']}: {row['n_valid']} of {row['n_candidates']} candidates valid; {rejections}")


if __name__ == "__main__":
    main()
