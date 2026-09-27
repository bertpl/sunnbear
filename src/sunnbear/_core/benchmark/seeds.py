"""Every random choice in a benchmark run draws from a seed derived from the run's root seed.

A derived seed depends only on the root seed, the purpose it serves, the test function, and the sample,
so it does not depend on the order in which samples run, the process that runs them, or whether the
run was resumed.
"""

import hashlib
import json
from enum import StrEnum


class SeedPurpose(StrEnum):
    """`SeedPurpose` names what a derived seed is used for, so 2 consumers never draw from the same seed."""

    CORRECTNESS_CHECK = "correctness_check"


def derive_seed(root_seed: int, purpose: SeedPurpose, function_id: str, sample_idx: int) -> int:
    """Return the seed for 1 purpose, test function and sample of a run: an integer in `[0, 2^64)`.

    The seed is the first 8 bytes of the SHA-256 digest of the 4 values, encoded as a JSON list, so no
    function id can make 2 different sets of values encode to the same bytes.
    """
    payload = json.dumps([root_seed, str(purpose), function_id, sample_idx]).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
