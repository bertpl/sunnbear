"""This package selects the pipeline's suites: the most diverse candidates under difficulty quotas.

Core selection and distillation select every suite of the benchmark suite pipeline with the same parts, so that every
suite is selected by the same objective in the same space:

- `DifficultyClass`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_class`;
- `SuiteComposition`, a suite's difficulty quotas, each a `DifficultyQuota`, in `suite_composition`;
- `CandidatePool`, the candidates that a suite is selected from, in `candidate_pool`;
- `select_diverse_suite`, which selects the most diverse suite of a composition from a `CandidatePool` by max-div, in
  `diverse_selection`.

This package imports nothing from its sibling package `stages`, which imports from this package.
"""

from .candidate_pool import CandidatePool
from .difficulty_class import EDI_GPQ_LEVEL, DifficultyClass
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, select_diverse_suite
from .suite_composition import DifficultyQuota, SuiteComposition
