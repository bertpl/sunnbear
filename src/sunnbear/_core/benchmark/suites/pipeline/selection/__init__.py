"""This package selects the pipeline's suites: the most diverse candidates under difficulty quotas.

Core selection and distillation select every suite of the benchmark suite pipeline with the parts below, so that every
suite is selected by the same objective in the same feature space:

- `DifficultyTier`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_tier`;
- `DifficultyTierQuotas`, the quotas of 1 selection, each on a group of tiers, in `difficulty_tier_quotas`;
- `CandidatePool`, the input candidates of a selection, in `candidate_pool`;
- `select_diverse_problem_ids`, which selects the most diverse candidates of a `CandidatePool` by max-div, under a
  `DifficultyTierQuotas`, in `diverse_selection`.

This package imports nothing from the packages `state` and `stages` beside it, which import from this package.
"""

from .candidate_pool import CandidatePool
from .difficulty_tier import DifficultyTier
from .difficulty_tier_quotas import DifficultyTierQuotas
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, select_diverse_problem_ids
