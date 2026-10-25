"""`CRangeCalibrationTask` calibrates the c-ranges of a batch of candidates, in a worker process or in this process."""

from dataclasses import dataclass

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.problems.core import FormulaRegistry

from .c_range_calibration import CRange, calibrate_c_range
from .rejection_reason import RejectionReason


# ==================================================================================================
#  CRangeCalibrationTask
# ==================================================================================================
@dataclass(frozen=True)
class CRangeCalibrationTask:
    """A `CRangeCalibrationTask` calibrates the c-range of each candidate in `problem_ids`, rebuilt from its id.

    Attributes:
        problem_ids: The ids of the candidates, each as rendered by `ProblemId`.
    """

    problem_ids: tuple[str, ...]

    def run(self) -> list[CRange | RejectionReason]:
        """Return each candidate's c-range, or the reason that calibration rejects it, in the order of `problem_ids`.

        Calibration checks the c-values of the largest size of the shipped tuple set, as `calibrate_c_range` requires.
        """
        mc_tuples = load_mc_tuples(max(MCTuplesSize))
        candidates = [FormulaRegistry.candidate_from_id(problem_id) for problem_id in self.problem_ids]
        return [
            calibrate_c_range(candidate.xc_fun, candidate.a, candidate.b, mc_tuples=mc_tuples)
            for candidate in candidates
        ]
