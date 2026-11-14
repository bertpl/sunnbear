import pytest

from sunnbear._core.problems.core import CandidateTestProblem, ProblemId
from sunnbear._core.problems.core import (
    TestProblem as _TestProblem,  # The underscore alias keeps pytest from collecting the class.
)

from .example_formulas import ExampleCubic

PROBLEM_ID = ProblemId((99, 801), ("p1",), (0.2,))


# ==================================================================================================
#  Well-definedness
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])  # reversed and degenerate are both ill-defined
def test_candidate_rejects_ill_defined_bracket(a, b):
    with pytest.raises(ValueError, match="a < b"):
        CandidateTestProblem(id=PROBLEM_ID, formula=ExampleCubic(), a=a, b=b)


@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])
def test_calibrated_type_rejects_ill_defined_bracket(a, b):
    with pytest.raises(ValueError, match="a < b"):
        _TestProblem(id=PROBLEM_ID, formula=ExampleCubic(), a=a, b=b, c_min=-1.0, c_max=1.0)


@pytest.mark.parametrize("c_min, c_max", [(1.0, -1.0), (0.0, 0.0)])  # reversed and degenerate c-ranges
def test_calibrated_rejects_ill_defined_c_range(c_min, c_max):
    # --- arrange ----------------------
    candidate = CandidateTestProblem(id=PROBLEM_ID, formula=ExampleCubic(), a=-2.0, b=2.0)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="c_min < c_max"):
        candidate.calibrated(c_min, c_max)
