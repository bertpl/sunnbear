"""Generate the shipped (u, v) tuple set and save it as the `mc_tuples` data artifact.

The maintainer runs this script by hand whenever the tuple set is regenerated, never at release
time. The script:

- calls `sunnbear.benchmark.generate_mc_tuples`;
- prints the spread of every size;
- saves the set through `ArtifactStore`, which records in the artifact's manifest the
  `generate_mc_tuples` call, its arguments and max-div's version.

Usage:

    uv run python scripts/generate_mc_tuples.py --t-total-sec 900
"""

import argparse
import importlib.metadata

from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.mc_tuples import MCTuplesDeclaration, MCTuplesSize, generate_mc_tuples


def main() -> None:
    """Generate the tuple set, print each size's spread, and save it as the `mc_tuples` artifact."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--t-total-sec", type=float, required=True, help="total wall-clock time of the solves")
    parser.add_argument("--n-workers", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    arguments = {"t_total_sec": args.t_total_sec, "n_workers": args.n_workers, "seed": args.seed}
    tuples = generate_mc_tuples(**arguments)

    print("| size | L2 | u | v | max bin deviation |")
    print("|---|---|---|---|---|")
    for size in MCTuplesSize:
        stats = tuples.first(size).stats()
        print(
            f"| {size} | {stats.min_separation_l2_fraction:.1%} | {stats.min_separation_u_fraction:.1%} "
            f"| {stats.min_separation_v_fraction:.1%} | {stats.max_bin_count_deviation:g} |"
        )

    manifest = ArtifactStore.save(
        MCTuplesDeclaration,
        tuples,
        built_with={"max-div": importlib.metadata.version("max-div")},
        generated_by={"function": "sunnbear.benchmark.generate_mc_tuples", "arguments": arguments},
    )
    print(f"Saved {manifest.short_identity}.")


if __name__ == "__main__":
    main()
