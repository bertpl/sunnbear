"""This package selects the pipeline's suites: the most diverse candidates under difficulty quotas.

Core selection and distillation select every suite of the benchmark suite pipeline with the parts below, so that every
suite is selected by the same objective in the same feature space:

- `DifficultyClass`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_class`;
- `SuiteComposition`, a suite's difficulty quotas, each a `DifficultyQuota`, in `suite_composition`;
- `CoreComposition`, the size and difficulty quotas of the largest Core that the candidates can fill, in
  `core_composition`;
- `SuiteFamily`, which names a family of the suites distilled from the Core, in `suite_family`;
- `CandidatePool`, the input candidates of a suite's selection, in `candidate_pool`;
- `select_diverse_suite`, which selects the most diverse suite of a composition from a `CandidatePool` by max-div, as
  a `DiverseSuite`, in `diverse_selection`.

This package imports nothing from the packages `state` and `stages` beside it, which import from this package.
"""

from .candidate_pool import CandidatePool
from .core_composition import CORE_SIZES, MAX_CORE_SIZE, CoreComposition, CoreCompositionWarning
from .difficulty_class import DifficultyClass
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, DiverseSuite, select_diverse_suite
from .suite_composition import DifficultyQuota, SuiteComposition
from .suite_family import SuiteFamily
