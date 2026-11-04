"""`compute_edi` computes a candidate's empirical difficulty index (EDI) from its solves.

A candidate's EDI is the geometric pseudo-quantile (`gpq`) at `EDI_GPQ_LEVEL` of the `n_fevals_eff` of all its solves
with the core solver configs, each incorrect solve counting as `max_fevals`, the evaluation budget of a solve. At level
0.5, the gpq is the geometric mean.

The EDI is stored apart from the feature vector, so that the EDI does not depend on which gpq levels the feature
vector holds. A feature vector that holds the gpq at `EDI_GPQ_LEVEL` holds the same value there.
"""

import numpy as np

from sunnbear._core.stats import gpq

EDI_GPQ_LEVEL = 0.5


def compute_edi(n_fevals_eff: np.ndarray) -> float:
    """Return the EDI of a candidate whose solves spent `n_fevals_eff`, an array of any shape over all its solves.

    `n_fevals_eff` must count each incorrect solve as `max_fevals`, the evaluation budget of a solve.
    """
    return gpq(n_fevals_eff.ravel(), EDI_GPQ_LEVEL)
