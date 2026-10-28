"""Every random choice in a benchmark run, or in a snuffled analysis of the pipeline, draws from a derived seed.

A derived seed depends only on:

- the root seed;
- the seed's purpose;
- the test problem;
- the Monte Carlo sample.

It is therefore the same regardless of:

- the order in which Monte Carlo samples run;
- the process that runs them;
- whether the run was resumed.
"""

import hashlib
import json
from enum import StrEnum


class SeedPurpose(StrEnum):
    """`SeedPurpose` names what a derived seed is used for, so 2 consumers never draw from the same seed."""

    CORRECTNESS_CHECK = "correctness_check"
    SNUFFLED_ANALYSIS = "snuffled_analysis"


def derive_seed(*, root_seed: int, purpose: SeedPurpose, problem_id: str, mc_sample_idx: int) -> int:
    """Return the seed for a given purpose, test problem and Monte Carlo sample of a run: an integer in `[0, 2^64)`.

    The arguments are encoded as a JSON list before hashing, because JSON quotes and escapes the problem id,
    so no problem id can make 2 different sets of arguments encode to the same bytes.

    Args:
        root_seed: The run's root seed; every seed of the run is derived from it.
        purpose: What the seed is used for, so that 2 consumers never draw from the same seed.
        problem_id: The id of the test problem, so that each test problem draws its own values.
        mc_sample_idx: The index of the Monte Carlo sample, the (u, v) tuple in the tuple set, so that each
            sample of a test problem draws its own values. The sizes of the tuple set are nested, so a
            sample keeps its index, and therefore its seed and verdict, whatever the run's size.
    """
    encoded_args = json.dumps([root_seed, str(purpose), problem_id, mc_sample_idx]).encode()
    return int.from_bytes(hashlib.sha256(encoded_args).digest()[:8], "big")
