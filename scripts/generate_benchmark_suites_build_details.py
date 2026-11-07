"""Run the benchmark suite pipeline over the shipped test problems, and save and publish its build details.

The artifact is `benchmark_suites_build_details`. The maintainer runs this script, through
``make benchmark-suites-build-details``, when the release script reports that the shipped build details are stale, and
then commits the artifact's manifest. The script:

- runs the pipeline in `PipelineMode.DRAFT` over every registered formula, into the workspace directory given by
  ``--workspace``, because the benchmark suites that it builds are not shipped yet, so a run of a few minutes suffices;
- stops with status 1, without saving, when a stage stops the run, because the build details of a stopped run hold no
  benchmark suites;
- saves the build details through `ArtifactStore`, which records in the artifact's manifest how they were built and
  from which `mc_tuples` artifact;
- publishes the artifact's data release, unless ``--no-publish`` is given for a trial run.

Usage, with the workspace directory under ``script_outputs/``:

    make benchmark-suites-build-details
"""

import argparse
import importlib.metadata
from pathlib import Path

from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.mc_tuples import MCTuplesDeclaration
from sunnbear._core.benchmark.suites.pipeline import (
    BenchmarkSuitesBuildDetailsDeclaration,
    PipelineMode,
    run_pipeline,
)
from sunnbear._core.problems.core import FormulaRegistry

_MODE = PipelineMode.DRAFT


def main() -> None:
    """Run the pipeline, then save and publish its build details as the `benchmark_suites_build_details` artifact."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", type=Path, required=True, help="directory for the outputs of the stages")
    parser.add_argument("--n-workers", type=int, help="number of worker processes (default: 1 per logical CPU)")
    parser.add_argument(
        "--no-publish",
        action="store_true",
        dest="is_publish_skipped",
        help="save the artifact, but publish no data release",
    )
    args = parser.parse_args()

    result = run_pipeline(
        workspace_dir=args.workspace, formulas=FormulaRegistry.formulas(), n_workers=args.n_workers, mode=_MODE
    )
    for manifest in result.manifests:
        print(f"{manifest.stage_id}: {manifest.n_candidates_out} of {manifest.n_candidates_in} candidates kept")
    if result.build_details.stop is not None:
        print(f"{result.build_details.stop.stage_id}: stopped: {result.build_details.stop.reason}")
        print("Not saved: the run stopped.")
        raise SystemExit(1)

    manifest = ArtifactStore.save(
        BenchmarkSuitesBuildDetailsDeclaration,
        result.build_details,
        built_with={package: importlib.metadata.version(package) for package in ("max-div", "snuffled")},
        input_artifact_hashes={MCTuplesDeclaration.name: ArtifactStore.load_manifest(MCTuplesDeclaration).content_hash},
        generated_by={
            "function": "sunnbear._core.benchmark.suites.pipeline.run_pipeline",
            "arguments": {"mode": _MODE.name, "n_workers": args.n_workers},
        },
    )
    print(f"Saved {manifest.short_identity}.")
    if args.is_publish_skipped:
        print("Not published (--no-publish).")
    else:
        manifest = ArtifactStore.publish(BenchmarkSuitesBuildDetailsDeclaration)
        print(f"Published {manifest.short_identity}; commit its manifest.")


if __name__ == "__main__":
    main()
