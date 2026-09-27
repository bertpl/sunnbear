"""Every random choice in a benchmark run draws from a seed derived from the run's root seed.

A derived seed depends only on the root seed, the seed's purpose, the test function and the sample. It is
therefore the same regardless of:

- the order in which samples run;
- the process that runs them;
- whether the run was resumed.
"""

import hashlib
import json
from enum import StrEnum


class SeedPurpose(StrEnum):
    """`SeedPurpose` names what a derived seed is used for, so 2 consumers never draw from the same seed."""

    CORRECTNESS_CHECK = "correctness_check"


def derive_seed(root_seed: int, purpose: SeedPurpose, function_id: str, sample_idx: int) -> int:
    """Return the seed for 1 purpose, test function and sample of a run: an integer in `[0, 2^64)`.

    The seed is the first 8 bytes of the SHA-256 digest of the arguments, encoded as a JSON list. JSON
    quotes and escapes the function id, so no function id can make 2 different sets of arguments encode
    to the same bytes.
    """
    payload = json.dumps([root_seed, str(purpose), function_id, sample_idx]).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
