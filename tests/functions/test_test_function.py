import pytest

from sunnbear._core.functions.catalog.c02_documented_functions.c01_polynomials.f01_cubic import Cubic
from sunnbear.functions import CandidateTestFunction, FunctionId, ParamValue
from sunnbear.functions import TestFunction as _TestFunction  # underscore alias: keep pytest from collecting it

FID = FunctionId((2, 1, 1), (ParamValue.decimal(0.2),))


# ==================================================================================================
#  Well-definedness
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])  # reversed and degenerate are both ill-defined
def test_candidate_rejects_ill_defined_bracket(a, b):
    with pytest.raises(ValueError, match="a < b"):
        CandidateTestFunction(id=FID, formula=Cubic(), a=a, b=b)


@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])
def test_calibrated_type_rejects_ill_defined_bracket(a, b):
    with pytest.raises(ValueError, match="a < b"):
        _TestFunction(id=FID, formula=Cubic(), a=a, b=b, c_min=-1.0, c_max=1.0)


@pytest.mark.parametrize("c_min, c_max", [(1.0, -1.0), (0.0, 0.0)])  # reversed and degenerate c-ranges
def test_calibrated_rejects_ill_defined_c_range(c_min, c_max):
    # --- arrange ----------------------
    candidate = CandidateTestFunction(id=FID, formula=Cubic(), a=-2.0, b=2.0)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="c_min < c_max"):
        candidate.calibrated(c_min, c_max)
