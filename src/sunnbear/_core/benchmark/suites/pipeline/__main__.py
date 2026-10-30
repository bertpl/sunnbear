"""Run the benchmark suite pipeline over the shipped formulas, into the workspace directory given by ``--workspace``.

From the repository root, maintainers run it into a folder under `script_outputs/`::

    uv run python -m sunnbear._core.benchmark.suites.pipeline --workspace script_outputs/pipeline

The workspace has no default directory, because the shipped package cannot assume that the repository's folders
exist. ``--n-workers`` sets the number of worker processes that the stages share. The candidates are characterized by
the solves of the built-in solver configs whose role marks them for characterizing test problems.

After the run, the command prints 1 line per stage that wrote its output, then, for each stage that rejects candidates:

- the stage's output name, then the number of formulas with rejected candidates;
- 1 line per such formula.

When a stage stops the run, for example because core selection finds too few candidates for the smallest Core of the
benchmark suites, the command then prints that stage's output name and the reason, and exits with status 1.
"""

import argparse
from pathlib import Path

from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.solvers import bracketing  # noqa: F401 - importing the shipped solvers registers their configs
from sunnbear._core.solvers.core import SolverConfigRegistry

from .core import REJECTIONS_PER_FORMULA_REPORT_NAME, PipelineWorkspace, summarize_rejections_per_formula
from .runner import run_pipeline


def main() -> None:
    """Parse the command line, run the pipeline, and print what each stage wrote, the rejections and any stop."""
    parser = argparse.ArgumentParser(
        prog="python -m sunnbear._core.benchmark.suites.pipeline",
        description="Run the benchmark suite pipeline over the shipped formulas.",
    )
    parser.add_argument("--workspace", type=Path, required=True, help="directory for the outputs of the stages")
    parser.add_argument("--n-workers", type=int, help="number of worker processes (default: 1 per logical CPU)")
    args = parser.parse_args()

    result = run_pipeline(
        workspace_dir=args.workspace,
        formulas=FormulaRegistry.formulas(),
        core_solver_configs=[
            config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
        ],
        n_workers=args.n_workers,
    )
    for manifest in result.manifests:
        report_names = ", ".join(manifest.report_sha256s) or "none"
        rows = f"{manifest.n_rows} rows, {manifest.n_dropped_rows} dropped"
        print(f"{manifest.output_name}: {rows}, in {manifest.duration_sec:.2f} s; reports: {report_names}")
    for manifest in result.manifests:
        if REJECTIONS_PER_FORMULA_REPORT_NAME in manifest.report_sha256s:
            rejections_per_formula = PipelineWorkspace(args.workspace).read_report(
                manifest.output_name, REJECTIONS_PER_FORMULA_REPORT_NAME
            )
            [count_line, *formula_lines] = summarize_rejections_per_formula(rejections_per_formula)
            print(f"{manifest.output_name}: {count_line}")
            for line in formula_lines:
                print(line)
    if result.stop is not None:
        print(f"{result.stop.output_name}: stopped: {result.stop.reason}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
