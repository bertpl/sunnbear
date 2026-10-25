"""`FunctionEvaluatingChecksTask` runs the checks that evaluate f on a batch of candidates.

These checks are c-range calibration and then the bisection count check, which needs the c-range. Both checks run in 1
task, so the worker that compiles a formula for calibration also runs the bisection count check on it, and each formula
is compiled in only 1 worker. The task runs in a worker process of the pool, or in the calling process.
"""

from dataclasses import dataclass

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.problems.core import CandidateTestProblem, FormulaRegistry

from .bisection_count_check import is_bisection_count_exact
from .c_range_calibration import calibrate_c_range
from .rejection_reason import RejectionReason


# ==================================================================================================
#  FunctionEvaluatingChecksTask
# ==================================================================================================
@dataclass(frozen=True)
class FunctionEvaluatingChecksTask:
    """A `FunctionEvaluatingChecksTask` runs the checks that evaluate f on each candidate in `problem_ids`.

    Attributes:
        problem_ids: The ids of the candidates, each as rendered by `ProblemId`; the task rebuilds each candidate from
            its id.
    """

    problem_ids: tuple[str, ...]

    def run(self) -> list[CRange | RejectionReason]:
        """Return each candidate's c-range, or the reason that a check rejects it, in the order of `problem_ids`.

        Calibration uses the largest size of the shipped tuple set, as `calibrate_c_range` requires.
        """
        mc_tuples = load_mc_tuples(max(MCTuplesSize))
        return [
            self._check_candidate(FormulaRegistry.candidate_from_id(problem_id), mc_tuples=mc_tuples)
            for problem_id in self.problem_ids
        ]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _check_candidate(candidate: CandidateTestProblem, *, mc_tuples: MCTuples) -> CRange | RejectionReason:
        """Return the candidate's c-range, or the reason that calibration or the bisection count check rejects it."""
        c_range = calibrate_c_range(candidate.xc_fun, candidate.a, candidate.b, mc_tuples=mc_tuples)
        if isinstance(c_range, RejectionReason):
            return c_range
        elif not is_bisection_count_exact(candidate.calibrated(c_range.c_min, c_range.c_max)):
            return RejectionReason.BISECTION_COUNT_NOT_EXACT
        else:
            return c_range
