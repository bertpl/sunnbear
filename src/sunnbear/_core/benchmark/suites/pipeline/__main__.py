"""Run the benchmark suite pipeline over the shipped formulas, into the workspace directory given by ``--workspace``.

From the repository root, maintainers run it into a folder under `script_outputs/`::

    uv run python -m sunnbear._core.benchmark.suites.pipeline --workspace script_outputs/pipeline

The workspace has no default directory, because the shipped package cannot assume that the repository's folders exist.
The candidates are characterized by the solves of the built-in solver configs whose role marks them for characterizing
test problems.

The command also takes these optional flags:

- ``--n-workers`` sets the number of worker processes that the stages share;
- ``--draft`` runs the stages in `PipelineMode.DRAFT`, which takes a fraction of a full run's time and applies the same
  selection rules.

After the run, the command prints 1 line per stage that ran to its end: the number of candidates that it received and
kept, and its run time.

When a stage stops the run, for example because core selection finds too few candidates for the smallest Core of the
benchmark suites, the command then prints that stage's id and the reason, and exits with status 1.
"""

import argparse
from pathlib import Path

from sunnbear._core.problems.core import FormulaRegistry

from .mode import PipelineMode
from .runner import run_pipeline


def main() -> None:
    """Parse the command line, run the pipeline, and print what each stage kept and any stop."""
    parser = argparse.ArgumentParser(
        prog="python -m sunnbear._core.benchmark.suites.pipeline",
        description="Run the benchmark suite pipeline over the shipped formulas.",
    )
    parser.add_argument("--workspace", type=Path, required=True, help="directory for the outputs of the stages")
    parser.add_argument("--n-workers", type=int, help="number of worker processes (default: 1 per logical CPU)")
    parser.add_argument(
        "--draft", dest="is_draft", action="store_true", help="do less work in the slowest stages, for a quick rerun"
    )
    args = parser.parse_args()

    result = run_pipeline(
        workspace_dir=args.workspace,
        formulas=FormulaRegistry.formulas(),
        n_workers=args.n_workers,
        mode=PipelineMode.DRAFT if args.is_draft else PipelineMode.FULL,
    )
    for manifest in result.manifests:
        print(
            f"{manifest.stage_id}: {manifest.n_candidates_out} of {manifest.n_candidates_in} candidates kept, "
            f"in {manifest.duration_sec:.2f} s"
        )
    if result.stop is not None:
        print(f"{result.stop.stage_id}: stopped: {result.stop.reason}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
