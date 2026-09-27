"""Every random choice in a benchmark run draws from a seed derived from the run's root seed.

A derived seed depends only on:

- the root seed;
- the seed's purpose;
- the test function;
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


def derive_seed(*, root_seed: int, purpose: SeedPurpose, function_id: str, mc_sample_idx: int) -> int:
    """Return the seed for a given purpose, test function and Monte Carlo sample of a run: an integer in `[0, 2^64)`.

    The arguments are encoded as a JSON list before hashing, because JSON quotes and escapes the function id,
    so no function id can make 2 different sets of arguments encode to the same bytes.

    Args:
        root_seed: The run's root seed; every seed of the run is derived from it.
        purpose: What the seed is used for, so that 2 consumers never draw from the same seed.
        function_id: The id of the test function, so that each test function draws its own values.
        mc_sample_idx: The index of the Monte Carlo sample, the (u, v) tuple in the tuple set, so that each
            sample of a test function draws its own values. The sizes of the tuple set are nested, so a
            sample keeps its index, and therefore its seed and verdict, whatever the run's size.
    """
    encoded_args = json.dumps([root_seed, str(purpose), function_id, mc_sample_idx]).encode()
    return int.from_bytes(hashlib.sha256(encoded_args).digest()[:8], "big")
