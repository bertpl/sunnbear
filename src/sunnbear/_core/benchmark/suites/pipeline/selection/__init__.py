"""This package selects the pipeline's suites: the most diverse candidates under difficulty quotas.

Suite selection selects every benchmark suite of the pipeline with the parts below, so that every suite is selected by
the same objective in the same feature space:

- `DifficultyTier`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_tier`;
- `DifficultyTierQuotas`, the quota of each tier in 1 selection, in `difficulty_tier_quotas`;
- `CandidatePool`, the input candidates of a selection, in `candidate_pool`;
- `DifficultyTierAssignment`, which gives each candidate of a pool the tier whose quota it counts toward in 1
  selection, in `difficulty_tier_assignment`;
- `select_diverse_problem_ids`, which selects the most diverse candidates of a `CandidatePool` by max-div, under a
  `DifficultyTierQuotas` and the tiers of a `DifficultyTierAssignment`, in `diverse_selection`;
- `compute_diversity_score`, which scores a set of candidates by the objective of `select_diverse_problem_ids`, in
  `diverse_selection`.

This package imports nothing from the packages `state` and `stages` beside it, which import from this package.
"""

from .candidate_pool import CandidatePool
from .difficulty_tier import DifficultyTier
from .difficulty_tier_assignment import DifficultyTierAssignment
from .difficulty_tier_quotas import DifficultyTierQuotas
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, compute_diversity_score, select_diverse_problem_ids
