"""Generate the shipped (u, v) tuple set and save it as the `mc_tuples` data artifact.

The maintainer runs this script by hand whenever the tuple set is regenerated, never at release
time. The script:

- calls `sunnbear.benchmark.generate_mc_tuples`;
- prints 1 line per solve as the construction goes, with the solve's budget, wall time and min separation fractions
  (as `MCTuplesStats` defines them);
- with `--inspection-dir`, stores each solve in that directory: its tuples as the CSV file `k<size>_<step>.csv`,
  and max-div's solution, with its score checkpoints, as the pickle file `k<size>_<step>_solution.pkl`;
- prints the spread of every size, and whether it holds exactly 1 tuple per lane, as
  `LaneGrid.is_one_per_lane_on_rebuilt_grid` checks it;
- saves the set through `ArtifactStore`, which records in the artifact's manifest the
  `generate_mc_tuples` call, its arguments and max-div's version; `--no-save` skips saving the set, for a trial run.

Usage:

    uv run python scripts/generate_mc_tuples.py --t-total-sec 43200 --inspection-dir local/regeneration
"""

import argparse
import importlib.metadata
import pickle
from pathlib import Path

import numpy as np

from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.mc_tuples import (
    MCTuplesDeclaration,
    MCTuplesSize,
    MCTuplesStats,
    MCTuplesStepResult,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid


def main() -> None:
    """Generate the tuple set, print each solve and each size's spread, and save the set as the `mc_tuples` artifact."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--t-total-sec", type=float, required=True, help="total wall-clock time of the solves")
    parser.add_argument("--n-workers", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-size",
        type=int,
        default=int(max(MCTuplesSize)),
        choices=[int(size) for size in MCTuplesSize],
        help="the largest size to build, for a trial run of the smaller sizes",
    )
    parser.add_argument("--inspection-dir", type=Path, help="directory for the tuples and solution of each solve")
    parser.add_argument(
        "--no-save", action="store_true", dest="is_trial_run", help="do not save the artifact, for a trial run"
    )
    args = parser.parse_args()

    arguments = {
        "t_total_sec": args.t_total_sec,
        "n_workers": args.n_workers,
        "seed": args.seed,
        "max_size": MCTuplesSize(args.max_size),
    }
    tuples = generate_mc_tuples(**arguments, on_step_finished=lambda result: report_step(result, args.inspection_dir))

    print("| size | L2 | u | v | 1 per lane |")
    print("|---|---|---|---|---|")
    for size in (size for size in MCTuplesSize if size <= tuples.size):
        size_tuples = tuples.first(size)
        stats = size_tuples.stats()
        print(
            f"| {size} | {stats.min_separation_l2_fraction:.1%} | {stats.min_separation_u_fraction:.1%} "
            f"| {stats.min_separation_v_fraction:.1%} | {LaneGrid.is_one_per_lane_on_rebuilt_grid(size_tuples)} |"
        )

    if args.is_trial_run:
        print("Not saved (--no-save).")
    else:
        manifest = ArtifactStore.save(
            MCTuplesDeclaration,
            tuples,
            built_with={"max-div": importlib.metadata.version("max-div")},
            generated_by={"function": "sunnbear.benchmark.generate_mc_tuples", "arguments": arguments},
        )
        print(f"Saved {manifest.short_identity}.")


def report_step(result: MCTuplesStepResult, inspection_dir: Path | None) -> None:
    """Print the step's budget, wall time and separation fractions, and store it in `inspection_dir` if given."""
    stats = MCTuplesStats(result.tuple_array)
    print(
        f"k={int(result.size)} {result.kind.value}: budget {result.t_budget_sec:.0f} s, "
        f"wall {result.t_wall_sec:.0f} s, L2 {stats.min_separation_l2_fraction:.1%}, "
        f"u {stats.min_separation_u_fraction:.1%}, v {stats.min_separation_v_fraction:.1%}",
        flush=True,
    )
    if inspection_dir is not None:
        inspection_dir.mkdir(parents=True, exist_ok=True)
        stem = f"k{int(result.size)}_{result.kind.value}"
        # 17 significant digits write every float64 so that `np.loadtxt` reads it back exactly.
        np.savetxt(
            inspection_dir / f"{stem}.csv", result.tuple_array, fmt="%.17g", delimiter=",", header="u,v", comments=""
        )
        with (inspection_dir / f"{stem}_solution.pkl").open("wb") as file:
            pickle.dump(result.solution, file)


if __name__ == "__main__":
    main()
