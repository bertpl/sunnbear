"""`SnuffledTier` names a budget of snuffled's analysis, and builds the analysis of a test problem at 1 tuple."""

from enum import Enum

from snuffled import Snuffler

from sunnbear._core.benchmark.protocol import MCSolveSettings, SeedPurpose, derive_seed
from sunnbear._core.problems.core import TestProblem

# Every snuffled analysis in the pipeline derives its seed from this root seed, so that its results are the same in
# every run of the pipeline.
ROOT_SEED = 0


# ==================================================================================================
#  SnuffledTier
# ==================================================================================================
class SnuffledTier(Enum):
    """A `SnuffledTier` names a budget of snuffled's analysis of 1 test problem at 1 tuple.

    Validation runs most of its analyses at LOW and a few at HIGH; coarse characterization runs at LOW, and full
    characterization at HIGH.

    Attributes:
        n_fun_samples: The number of x-values at which snuffled samples f across the interval.
        n_roots: The largest number of roots that snuffled analyzes.
        n_root_samples: The number of x-values at which snuffled samples f around each root that it analyzes.
    """

    LOW = (1_000, 30, 30)
    HIGH = (10_000, 100, 100)

    def __init__(self, n_fun_samples: int, n_roots: int, n_root_samples: int) -> None:
        self.n_fun_samples = n_fun_samples
        self.n_roots = n_roots
        self.n_root_samples = n_root_samples

    def build_snuffler(
        self, problem: TestProblem, *, mc_solve_settings: MCSolveSettings, mc_sample_idx: int
    ) -> Snuffler:
        """Return snuffled's analysis of `problem` at the tuple `mc_sample_idx` of `mc_solve_settings`, at this budget.

        The analysis covers f at the tuple's ``c`` over the problem's interval. snuffled's `dx`, the smallest scale at
        which it samples f, is the tuple's `xtol`: snuffled is designed to receive the solver's tolerance there.

        The analysis's seed derives from `ROOT_SEED`, the problem's id and `mc_sample_idx`, so the analysis is the same
        in every worker process and whatever order the analyses run in.
        """
        seed = derive_seed(
            root_seed=ROOT_SEED,
            purpose=SeedPurpose.SNUFFLED_ANALYSIS,
            problem_id=str(problem.id),
            mc_sample_idx=mc_sample_idx,
        )
        return Snuffler(
            problem.build_x_fun(float(mc_solve_settings.cs[mc_sample_idx])),
            problem.a,
            problem.b,
            dx=float(mc_solve_settings.xtols[mc_sample_idx]),
            # snuffled takes a seed that fits in an int64, and a derived seed can need 64 bits
            seed=seed % 2**63,
            n_fun_samples=self.n_fun_samples,
            n_roots=self.n_roots,
            n_root_samples=self.n_root_samples,
        )
