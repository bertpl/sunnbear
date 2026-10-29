"""`SnuffledAnalysisBudget` names a snuffled analysis budget and builds the analysis at 1 Monte Carlo tuple."""

from enum import Enum

from snuffled import Snuffler

from sunnbear._core.benchmark.protocol import MCSolveSettings, SeedPurpose, derive_seed
from sunnbear._core.problems.core import TestProblem

from .function_evaluation_error import FunctionEvaluationError

# Every snuffled analysis in the pipeline derives its seed from this root seed, so that its results are the same in
# every run of the pipeline.
SNUFFLED_ANALYSIS_ROOT_SEED = 0


# ==================================================================================================
#  SnuffledAnalysisBudget
# ==================================================================================================
class SnuffledAnalysisBudget(Enum):
    """A `SnuffledAnalysisBudget` names a budget of snuffled's analysis of 1 test problem at 1 Monte Carlo tuple.

    Attributes:
        n_fun_samples: The number of x-values at which snuffled samples f across the interval.
        n_roots: The largest number of roots that snuffled analyzes.
        n_root_samples: The number of x-values at which snuffled samples f around each root that it analyzes.
    """

    LOW = (1_000, 30, 30)
    HIGH = (10_000, 100, 100)

    def __init__(self, n_fun_samples: int, n_roots: int, n_root_samples: int) -> None:
        """Store the sample counts of the member's value as the budget's attributes."""
        self.n_fun_samples = n_fun_samples
        self.n_roots = n_roots
        self.n_root_samples = n_root_samples

    def build_snuffler(
        self, problem: TestProblem, *, mc_solve_settings: MCSolveSettings, mc_sample_idx: int
    ) -> Snuffler:
        """Return the analysis of `problem` at this budget, at tuple index `mc_sample_idx` of `mc_solve_settings`.

        The analysis covers f at the tuple's ``c`` over the problem's interval. snuffled's `dx` parameter, the smallest
        distance between 2 x-values at which snuffled samples f, is set to the tuple's `xtol`, because snuffled is
        designed to receive the solver's tolerance as `dx`.

        The analysis's seed derives from `SNUFFLED_ANALYSIS_ROOT_SEED`, the problem's id and `mc_sample_idx`, so the
        analysis is the same in every worker process and whatever order the analyses run in.

        When f raises during the analysis, the analysis raises `FunctionEvaluationError`, with f's exception as its
        cause, so that a caller can tell whether an exception came from f or from snuffled.
        """
        seed = derive_seed(
            root_seed=SNUFFLED_ANALYSIS_ROOT_SEED,
            purpose=SeedPurpose.SNUFFLED_ANALYSIS,
            problem_id=str(problem.id),
            mc_sample_idx=mc_sample_idx,
        )
        x_fun = problem.build_x_fun(float(mc_solve_settings.cs[mc_sample_idx]))

        def evaluate_f(x: float) -> float:
            """Return f at `x`, raising `FunctionEvaluationError` from any exception that f raises."""
            try:
                return x_fun(x)
            except Exception as exc:
                raise FunctionEvaluationError(f"f raised at x = {float(x)!r}") from exc

        return Snuffler(
            evaluate_f,
            problem.a,
            problem.b,
            dx=float(mc_solve_settings.xtols[mc_sample_idx]),
            # snuffled takes a seed that fits in a signed int64, and a derived seed lies in [0, 2**64)
            seed=seed % 2**63,
            n_fun_samples=self.n_fun_samples,
            n_roots=self.n_roots,
            n_root_samples=self.n_root_samples,
        )
