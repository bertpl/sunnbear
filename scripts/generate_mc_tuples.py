"""Generate the shipped (u, v) tuple set and save it as the `mc_tuples` data artifact.

The maintainer runs this script by hand whenever the tuple set is regenerated, never at release
time. The script:

- calls `sunnbear.benchmark.generate_mc_tuples`;
- prints 2 lines per size as the construction goes:
  - the solve's budget and wall time;
  - the allocation's predicted offsets of the mean;
  - what the mean correction did;
  - the size's spread before and after the correction, as `MCTuplesStats` defines it;
- with `--inspection-dir`, stores each size in that directory: its tuples after the mean correction as the CSV file
  `k<size>.csv`, its tuples before it as `k<size>_uncorrected.csv`, and max-div's solution, with its score
  checkpoints, as the pickle file `k<size>_solution.pkl`;
- prints the spread of every size, its means and its largest number of tuples in 1 fine lane, and the overall score;
- saves the set through `ArtifactStore`, which records in the artifact's manifest the
  `generate_mc_tuples` call, its arguments and max-div's version; `--no-save` skips saving the set, for a trial run.

Usage:

    uv run python scripts/generate_mc_tuples.py --t-total-sec 28800 --inspection-dir script_outputs/regeneration
"""

import argparse
import importlib.metadata
import math
import pickle
from pathlib import Path

import numpy as np

from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.mc_tuples import (
    N_FINE_LANES,
    MCTuplesDeclaration,
    MCTuplesSize,
    MCTuplesSizeResult,
    MCTuplesStats,
    fine_lanes_of,
    generate_mc_tuples,
)


def main() -> None:
    """Generate the tuple set, print each size and its spread, and save the set as the `mc_tuples` artifact."""
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
    parser.add_argument("--n-population", type=int, default=2**20, help="candidate tuples per size")
    parser.add_argument(
        "--allocation-epsilon",
        type=float,
        default=0.1,
        help=(
            "share by which the allocation of new tuples to the gaps between the size below's values may shrink the "
            "smallest distance between neighboring values on an axis, to bring the predicted mean closer to 0.5"
        ),
    )
    parser.add_argument("--inspection-dir", type=Path, help="directory for the tuples and solution of each size")
    parser.add_argument(
        "--no-save", action="store_true", dest="is_trial_run", help="do not save the artifact, for a trial run"
    )
    args = parser.parse_args()

    arguments = {
        "t_total_sec": args.t_total_sec,
        "n_workers": args.n_workers,
        "seed": args.seed,
        "max_size": MCTuplesSize(args.max_size),
        "n_population": args.n_population,
        "allocation_epsilon": args.allocation_epsilon,
    }
    tuples = generate_mc_tuples(**arguments, on_size_finished=lambda result: report_size(result, args.inspection_dir))

    print(
        "| size | min separation L2 / u / v | gpq(0.1) u / v / L2 | score | mean offset u / v | tuples per fine lane |"
    )
    print("|---|---|---|---|---|---|")
    scores = []
    for size in (size for size in MCTuplesSize if size <= tuples.size):
        size_tuples = tuples.first(size)
        stats = size_tuples.stats()
        scores.append(stats.score)
        offsets = [(values.mean() - 0.5) * N_FINE_LANES for values in (size_tuples.u, size_tuples.v)]
        max_per_lane = max(int(np.bincount(fine_lanes_of(values)).max()) for values in (size_tuples.u, size_tuples.v))
        print(
            f"| {size} | {stats.min_separation_l2_fraction:.1%} / {stats.min_separation_u_fraction:.1%} / "
            f"{stats.min_separation_v_fraction:.1%} | {stats.gpq_u_fraction:.1%} / {stats.gpq_v_fraction:.1%} / "
            f"{stats.gpq_l2_fraction:.1%} | {stats.score:.1%} | {offsets[0]:+.1e} / {offsets[1]:+.1e} | "
            f"at most {max_per_lane} |"
        )
    print(f"Overall score, the geomean of the sizes' scores: {math.exp(np.mean(np.log(scores))):.1%}")

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


def report_size(result: MCTuplesSizeResult, inspection_dir: Path | None) -> None:
    """Print the size's solve, allocation, correction and spread, and store it in `inspection_dir` if given."""
    before, after = MCTuplesStats(result.uncorrected_tuple_array), result.tuples.stats()
    axis_reports = []
    for label, allocation, correction in (
        ("u", result.gap_allocation.u, result.mean_correction.u),
        ("v", result.gap_allocation.v, result.mean_correction.v),
    ):
        if allocation.mean_aware_offset_fine_lanes is None:
            predicted = "1 gap"
        else:
            predicted = (
                f"predicted {allocation.greedy_offset_fine_lanes:+.2f} → {allocation.mean_aware_offset_fine_lanes:+.2f}"
            )
        axis_reports.append(
            f"{label}: {predicted}, offset {correction.offset_before_fine_lanes:+.3f} → "
            f"{correction.offset_after_fine_lanes:+.1e}, D {correction.cap * N_FINE_LANES:.2f}, "
            f"largest move {correction.max_move_fine_lanes:.2f}"
        )
    print(
        f"k={int(result.size)}: budget {result.t_budget_sec:.0f} s, wall {result.t_wall_sec:.0f} s; "
        f"in fine lanes, {'; '.join(axis_reports)}",
        flush=True,
    )
    print(
        f"  gpq(0.1) u / v / L2 and score, before → after the correction: "
        f"{format_spread(before)} → {format_spread(after)}",
        flush=True,
    )
    if inspection_dir is not None:
        inspection_dir.mkdir(parents=True, exist_ok=True)
        stem = f"k{int(result.size)}"
        for suffix, tuple_array in (("", result.tuples.tuple_array), ("_uncorrected", result.uncorrected_tuple_array)):
            # Writing 17 significant digits lets `np.loadtxt` read every float64 back exactly.
            np.savetxt(
                inspection_dir / f"{stem}{suffix}.csv",
                tuple_array,
                fmt="%.17g",
                delimiter=",",
                header="u,v",
                comments="",
            )
        with (inspection_dir / f"{stem}_solution.pkl").open("wb") as file:
            pickle.dump(result.solution, file)


def format_spread(stats: MCTuplesStats) -> str:
    """Return the 3 gpq(0.1) fractions and the score of a size."""
    return f"{stats.gpq_u_fraction:.1%} / {stats.gpq_v_fraction:.1%} / {stats.gpq_l2_fraction:.1%}, {stats.score:.1%}"


if __name__ == "__main__":
    main()
