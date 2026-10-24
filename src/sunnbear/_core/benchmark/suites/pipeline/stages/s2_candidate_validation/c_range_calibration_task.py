"""`CRangeCalibrationTask` calibrates the c-ranges of a batch of candidates, in a worker process or in this process."""

from dataclasses import dataclass

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.functions.core import FormulaRegistry

from .c_range_calibration import CRange, calibrate_c_range
from .rejection_reason import RejectionReason


# ==================================================================================================
#  CRangeCalibrationTask
# ==================================================================================================
@dataclass(frozen=True)
class CRangeCalibrationTask:
    """A `CRangeCalibrationTask` calibrates the c-range of each candidate in `function_ids`, rebuilt from its id.

    Attributes:
        function_ids: The ids of the candidates, each as rendered by `FunctionId`.
    """

    function_ids: tuple[str, ...]

    def run(self) -> list[CRange | RejectionReason]:
        """Return each candidate's c-range, or the reason that calibration rejects it, in the order of `function_ids`.

        Calibration checks the c-values of the largest size of the shipped tuple set, as `calibrate_c_range` requires.
        """
        mc_tuples = load_mc_tuples(max(MCTuplesSize))
        candidates = [FormulaRegistry.candidate_from_id(function_id) for function_id in self.function_ids]
        return [
            calibrate_c_range(candidate.xc_fun, candidate.a, candidate.b, mc_tuples=mc_tuples)
            for candidate in candidates
        ]
