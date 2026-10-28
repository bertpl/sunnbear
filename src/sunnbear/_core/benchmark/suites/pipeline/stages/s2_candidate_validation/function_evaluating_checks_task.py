"""`FunctionEvaluatingChecksTask` runs the checks that evaluate f on a batch of candidates.

These checks are c-range calibration, then the bisection count check and the snuffled diagnostics check, which need the
c-range.

All 3 run in 1 task, so the worker that compiles a formula for calibration also runs the other 2 checks on it, and each
formula is compiled in only 1 worker. The task runs in a worker process of the pool, or in the calling process.
"""

from dataclasses import dataclass

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.problems.core import CandidateTestProblem, FormulaRegistry

from .check2_c_range_calibration import calibrate_c_range
from .check3_bisection_count import is_bisection_count_exact
from .check4_snuffled_diagnostics import find_snuffled_rejection_reason
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
        """Return the candidate's c-range, or the reason that 1 of the checks that evaluate f rejects it."""
        c_range = calibrate_c_range(candidate.xc_fun, candidate.a, candidate.b, mc_tuples=mc_tuples)
        if isinstance(c_range, RejectionReason):
            return c_range
        else:
            problem = candidate.calibrated(c_range.c_min, c_range.c_max)
            if not is_bisection_count_exact(problem):
                return RejectionReason.BISECTION_COUNT_NOT_EXACT
            elif (snuffled_rejection_reason := find_snuffled_rejection_reason(problem)) is not None:
                return snuffled_rejection_reason
            else:
                return c_range
