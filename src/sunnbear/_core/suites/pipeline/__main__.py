"""Run the suite pipeline over the shipped formulas, into the workspace directory given by ``--workspace``.

From the repository root, maintainers run it into a folder under `script_outputs/`::

    uv run python -m sunnbear._core.suites.pipeline --workspace script_outputs/pipeline

The workspace has no default directory, because the shipped package cannot assume that the
repository's folders exist.
"""

import argparse
from pathlib import Path

from sunnbear._core.functions.core import FormulaRegistry

from .runner import run_pipeline


def main() -> None:
    """Parse the command line, run the pipeline, and print 1 line per stage."""
    parser = argparse.ArgumentParser(
        prog="python -m sunnbear._core.suites.pipeline", description="Run the suite pipeline over the shipped formulas."
    )
    parser.add_argument("--workspace", type=Path, required=True, help="directory for the outputs of the stages")
    args = parser.parse_args()

    for manifest in run_pipeline(workspace_dir=args.workspace, formulas=FormulaRegistry.formulas()):
        rejections = ", ".join(f"{count} by {reason}" for reason, count in sorted(manifest.rejection_counts.items()))
        timing = f"{manifest.n_rows} rows in {manifest.duration_sec:.2f} s"
        print(f"{manifest.stage}: {timing}; rejected: {rejections or 'none'}")


if __name__ == "__main__":
    main()
