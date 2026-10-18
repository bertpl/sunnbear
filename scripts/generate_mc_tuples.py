"""Generate the shipped (u, v) tuple set and save it as the `mc_tuples` data artifact.

The maintainer runs this script by hand whenever the tuple set is regenerated, never at release
time. The script:

- runs `MCTuplesGenerator`, as `sunnbear.benchmark.generate_mc_tuples` does, so that the script can report each size
  once that size is built;
- prints the arguments of its `MCTuplesGenerator` calls before the construction starts, so that the log records the
  arguments even when `--no-save` skips saving the set and its manifest;
- prints 3 lines per size as the construction goes:
  - line 1 holds:
    - the size's budget and wall time;
    - the allocation's predicted offsets of the mean;
    - what the first value correction did;
  - line 2 holds what the second value correction did;
  - line 3 holds the size's spread, as `MCTuplesStats` defines it, after each of these steps:
    - the selection solve;
    - the first value correction;
    - the refinement solve;
    - the second value correction;
- with `--inspection-dir`, stores each size in that directory as CSV files of its tuples and pickle files of max-div's
  solutions, with their score checkpoints:
  - `k<size>_selected.csv`, after the selection solve;
  - `k<size>_first_corrected.csv`, after the first value correction;
  - `k<size>_refined.csv`, after the refinement solve;
  - `k<size>.csv`, after the second value correction;
  - `k<size>_selection_solution.pkl` and `k<size>_refinement_solution.pkl`;
- prints the spread of every size, its means and its largest number of tuples in 1 fine lane, and the overall score;
- saves the set through `ArtifactStore`, which records in the artifact's manifest the `generate_mc_tuples` call with
  the arguments that the script passes to `MCTuplesGenerator`, and max-div's version; `--no-save` skips saving the
  set, for a trial run.

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
    DEFAULT_N_POPULATION,
    DEFAULT_N_REFINEMENT_RANDOM_CANDIDATES_PER_CELL,
    DEFAULT_N_WORKERS,
    DEFAULT_SEED,
    N_FINE_LANES,
    TARGET_MEAN,
    MCTuplesDeclaration,
    MCTuplesGenerator,
    MCTuplesSize,
    MCTuplesSizeResult,
    MCTuplesStats,
    fine_lanes_of,
)
from sunnbear._core.benchmark.mc_tuples.construction.correction import MCTuplesAxisValueCorrection


def main() -> None:
    """Generate the tuple set, print each size and its spread, and save the set as the `mc_tuples` artifact."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--t-total-sec", type=float, required=True, help="total wall-clock time of the solves")
    parser.add_argument("--n-workers", type=int, default=DEFAULT_N_WORKERS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--max-size",
        type=int,
        default=int(max(MCTuplesSize)),
        choices=[int(size) for size in MCTuplesSize],
        help="the largest size to build, for a trial run of the smaller sizes",
    )
    parser.add_argument("--n-population", type=int, default=DEFAULT_N_POPULATION, help="candidate tuples per size")
    parser.add_argument(
        "--n-refinement-random-candidates-per-cell",
        type=int,
        default=DEFAULT_N_REFINEMENT_RANDOM_CANDIDATES_PER_CELL,
        help="candidate tuples per fine cell of a new tuple in the refinement solve",
    )
    parser.add_argument("--inspection-dir", type=Path, help="directory for the tuples and solutions of each size")
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
        "n_refinement_random_candidates_per_cell": args.n_refinement_random_candidates_per_cell,
    }
    print("Arguments of the construction:")
    for name, value in arguments.items():
        print(f"  {name} = {value}", flush=True)
    generator = MCTuplesGenerator(
        n_workers=arguments["n_workers"],
        seed=arguments["seed"],
        n_population=arguments["n_population"],
        n_refinement_random_candidates_per_cell=arguments["n_refinement_random_candidates_per_cell"],
        on_size_finished=lambda result: report_size(result, args.inspection_dir),
    )
    tuples = generator.generate(arguments["t_total_sec"], arguments["max_size"])

    print(
        "| size | min separation L2 / u / v | gpq(0.1) u / v / L2 | score | mean offset u / v | tuples per fine lane |"
    )
    print("|---|---|---|---|---|---|")
    scores = []
    for size in (size for size in MCTuplesSize if size <= tuples.size):
        size_tuples = tuples.first(size)
        stats = size_tuples.stats()
        scores.append(stats.score)
        offsets = [(values.mean() - TARGET_MEAN) * N_FINE_LANES for values in (size_tuples.u, size_tuples.v)]
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
    """Print the size's solves, allocation, corrections and spread, and store it in `inspection_dir` if given."""
    spreads = [
        MCTuplesStats(result.selected_tuple_array),
        MCTuplesStats(result.first_value_correction.tuple_array),
        MCTuplesStats(result.refined_tuple_array),
        result.tuples.stats(),
    ]
    first_correction_reports, second_correction_reports = [], []
    for label, allocation, first_correction, second_correction in (
        ("u", result.gap_allocation.u, result.first_value_correction.u, result.second_value_correction.u),
        ("v", result.gap_allocation.v, result.first_value_correction.v, result.second_value_correction.v),
    ):
        if allocation.mean_aware_offset_fine_lanes is None:
            predicted = "1 gap"
        else:
            predicted = (
                f"predicted {allocation.greedy_offset_fine_lanes:+.2f} → {allocation.mean_aware_offset_fine_lanes:+.2f}"
            )
        first_correction_reports.append(f"{label}: {predicted}, {format_correction(first_correction)}")
        second_correction_reports.append(f"{label}: {format_correction(second_correction)}")
    print(
        f"k={int(result.size)}: budget {result.t_budget_sec:.0f} s, wall {result.t_wall_sec:.0f} s; "
        f"in fine lanes, {'; '.join(first_correction_reports)}",
        flush=True,
    )
    print(f"  after the refinement, in fine lanes, {'; '.join(second_correction_reports)}", flush=True)
    print(
        f"  gpq(0.1) u / v / L2 and score, after the selection → correction → refinement → correction: "
        f"{' → '.join(format_spread(stats) for stats in spreads)}",
        flush=True,
    )
    if inspection_dir is not None:
        inspection_dir.mkdir(parents=True, exist_ok=True)
        stem = f"k{int(result.size)}"
        for suffix, tuple_array in (
            ("_selected", result.selected_tuple_array),
            ("_first_corrected", result.first_value_correction.tuple_array),
            ("_refined", result.refined_tuple_array),
            ("", result.tuples.tuple_array),
        ):
            # Writing 17 significant digits lets `np.loadtxt` read every float64 back exactly.
            np.savetxt(
                inspection_dir / f"{stem}{suffix}.csv",
                tuple_array,
                fmt="%.17g",
                delimiter=",",
                header="u,v",
                comments="",
            )
        for solve_name, solution in (
            ("selection", result.selection_solution),
            ("refinement", result.refinement_solution),
        ):
            with (inspection_dir / f"{stem}_{solve_name}_solution.pkl").open("wb") as file:
                pickle.dump(solution, file)


def format_correction(correction: MCTuplesAxisValueCorrection) -> str:
    """Return what 1 value correction did on 1 axis, in fine lanes: its shift for a rotation, else its cap D."""
    if correction.rotation_shift is not None:
        shift_or_cap = f"shift {correction.rotation_shift * N_FINE_LANES:+.2f}"
    else:
        shift_or_cap = f"D {correction.cap * N_FINE_LANES:.2f}"
    return (
        f"offset {correction.offset_before_fine_lanes:+.3f} → {correction.offset_after_fine_lanes:+.1e}, "
        f"{shift_or_cap}, largest move {correction.max_move_fine_lanes:.2f}, {correction.n_nudged} nudged"
    )


def format_spread(stats: MCTuplesStats) -> str:
    """Return the 3 gpq(0.1) fractions and the score of a size."""
    return f"{stats.gpq_u_fraction:.1%} / {stats.gpq_v_fraction:.1%} / {stats.gpq_l2_fraction:.1%}, {stats.score:.1%}"


if __name__ == "__main__":
    main()
