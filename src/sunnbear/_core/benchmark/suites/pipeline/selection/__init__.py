"""This package selects the pipeline's suites: the most diverse candidates under quotas on groups of candidates.

Suite selection selects every benchmark suite of the pipeline with the parts below, so that every suite is selected by
the same objective in the same feature space:

- `DifficultyTier`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_tier`;
- `CandidatePool`, the input candidates of a selection, in `candidate_pool`;
- `CandidateGroup`, a labeled group of candidates for a quota, with `DifficultyTierCandidateGroup`, the candidates of
  some difficulty tiers, and `FormulaCategoryCandidateGroup`, the candidates whose formulas lie below 1 formula
  category, in `candidate_group`;
- `ShareQuota`, the smallest and the largest share of a selection that a group may hold, as a stage declares it, in
  `share_quota`;
- `CountQuota`, a `ShareQuota` turned into the smallest and the largest count of 1 selection, in `count_quota`;
- `QuotaFulfillment`, which records a quota's smallest and largest count and the number of selected candidates that
  count toward it, in `quota_fulfillment`;
- `select_diverse_problem_ids`, which selects the most diverse candidates of a `CandidatePool` by max-div under
  `ShareQuota`s, in `diverse_selection`;
- `compute_diversity_score`, which scores a set of candidates by the objective of `select_diverse_problem_ids`, in
  `diverse_selection`.

This package imports nothing from the packages `state` and `stages` beside it, which import from this package.
"""

from .candidate_group import CandidateGroup, DifficultyTierCandidateGroup, FormulaCategoryCandidateGroup
from .candidate_pool import CandidatePool
from .count_quota import CountQuota
from .difficulty_tier import DifficultyTier
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, compute_diversity_score, select_diverse_problem_ids
from .quota_fulfillment import QuotaFulfillment
from .share_quota import ShareQuota
