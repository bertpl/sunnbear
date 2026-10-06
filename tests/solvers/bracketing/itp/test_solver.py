"""These tests assert that `ITP` reproduces the evaluation counts of the ITP paper, and keeps within its bound on the
iteration count."""

import math

import pytest

from sunnbear.solvers import ITP, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic

# The paper's experiments solve every function on [-1, 1] with this xtol, where bisection needs `_N_BISECTION`
# iterations.
_XTOL = 1e-10
_N_BISECTION = 34


def _sawtooth(x: float) -> float:
    """Return the paper's sawtooth function, which crosses 0 on many teeth."""
    return 202.0 * x - 2.0 * math.floor((2.0 * x + 1e-2) / (2.0 * 1e-2)) - 0.1


def _geometric(x: float) -> float:
    """Return the paper's geometric function ``1 / (21x - 1)``, set to 0 at its pole."""
    if x == 1.0 / 21.0:
        return 0.0
    else:
        return 1.0 / (21.0 * x - 1.0)


def _warsaw(x: float) -> float:
    """Return the paper's Warsaw function, ``sin(1 / (x + 1))`` right of -1 and -1 elsewhere."""
    if x > -1.0:
        return math.sin(1.0 / (x + 1.0))
    else:
        return -1.0


def _circles(x: float) -> float:
    """Return the paper's circles function, which takes the sign of ``3x + 1`` and is 0 where ``3x + 1`` is 0."""
    sign = (3.0 * x + 1.0 > 0.0) - (3.0 * x + 1.0 < 0.0)
    return sign * (1.0 - math.sqrt(1.0 - (3.0 * x + 1.0) ** 2 / 81.0))


# Each entry holds a test function of the paper's Table 1, by its name there, and the iteration count of ITP in that
# table. The table excludes the evaluations at the interval bounds.
_PAPER_TABLE_1 = {
    "lambert": (lambda x: x * math.exp(x) - 1.0, 8),
    "trigonometric_1": (lambda x: math.tan(x - 0.1), 8),
    "trigonometric_2": (lambda x: math.sin(x) + 0.5, 8),
    "polynomial_1": (lambda x: 4.0 * x**5 + x**2 + 1.0, 18),
    "polynomial_2": (lambda x: x + x**10 - 1.0, 16),
    "exponential": (lambda x: math.pi**x - math.e, 8),
    "logarithmic": (lambda x: -math.log(abs(x - 10.0 / 9.0)), 7),
    "posynomial": (lambda x: 1.0 / 3.0 + math.copysign(abs(x) ** (1.0 / 3.0), x) + x**3, 32),
    "weierstrass": (
        lambda x: 0.001 + sum(math.sin(math.pi * i**3 * x / 2.0) / (math.pi * i**3) for i in range(1, 11)),
        9,
    ),
    "polynomial_fraction": (lambda x: (x + 2.0 / 3.0) / (x + 101.0 / 100.0), 21),
    "normal_cdf": (lambda x: 0.5 * (1.0 + math.erf((x - 1.0) / math.sqrt(2.0))) - math.sqrt(2.0) / 4.0, 8),
    "normal_pdf": (lambda x: math.exp(-0.5 * (x - 1.0) ** 2) / math.sqrt(2.0 * math.pi) - math.sqrt(2.0) / 4.0, 8),
    "polynomial_3": (lambda x: (x * 1e6 - 1.0) ** 3, 34),
    "exponential_polynomial": (lambda x: math.exp(x) * (x * 1e6 - 1.0) ** 3, 34),
    "tangent_polynomial": (lambda x: (x - 1.0 / 3.0) ** 2 * math.atan(x - 1.0 / 3.0), 34),
    "circles": (_circles, 23),
    "step_function": (lambda x: float(x > (1.0 - 1e6) / 1e6) * (1.0 + 1e6) / 1e6 - 1.0, 34),
    "geometric": (_geometric, 34),
    "truncated_polynomial": (lambda x: (x / 2.0) ** 2 + math.ceil(x / 2.0) - 0.5, 34),
    "staircase": (lambda x: math.ceil(10.0 * x - 1.0) + 0.5, 31),
    "noisy_line": (lambda x: x + math.sin(x * 1e6) / 10.0 + 1e-3, 19),
    "warsaw": (_warsaw, 12),
    "sawtooth": (_sawtooth, 10),
    "sawtooth_cube": (lambda x: _sawtooth(x) ** 3, 34),
}


# ==================================================================================================
#  The paper's results
# ==================================================================================================
@pytest.mark.parametrize("name", [name for name in _PAPER_TABLE_1 if name != "step_function"])
def test_the_iteration_counts_of_table_1_of_the_paper_are_reproduced(name):
    """On every function of the paper's Table 1 but the step function, the robust form with ``n_slack = 0`` takes as
    many iterations as the paper reports.

    The paper's table comes from the authors' MATLAB code, which is the robust form.

    On the step function, MATLAB's arithmetic gives the table 34 iterations where `ITP` takes 35, so the test leaves
    that function out.
    """
    # --- arrange ----------------------
    f, n_iterations = _PAPER_TABLE_1[name]

    # --- act --------------------------
    result = ITP(n_slack=0, is_robust=True).solve(f, -1.0, 1.0, xtol=_XTOL, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_iterations + 2)


# ==================================================================================================
#  The bound on the iteration count
# ==================================================================================================
@pytest.mark.parametrize("name", _PAPER_TABLE_1)
def test_the_robust_form_with_slack_stays_within_n_max_on_the_functions_of_the_paper(name):
    """On every function of the paper's Table 1, the robust form with ``n_slack = 4`` takes at most
    ``n_max = 34 + 4`` iterations."""
    # --- arrange ----------------------
    f, _ = _PAPER_TABLE_1[name]

    # --- act --------------------------
    result = ITP(n_slack=4, is_robust=True).solve(f, -1.0, 1.0, xtol=_XTOL, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals - 2 <= _N_BISECTION + 4


@pytest.mark.parametrize(
    "name, is_robust",
    [
        ("polynomial_2", False),  # Rounding errors in the projection radius cause this overshoot.
        ("step_function", True),  # The robust form reduces overshoots but does not prevent them all.
    ],
)
def test_rounding_errors_can_push_either_form_past_n_max(name, is_robust):
    """Without slack, rounding errors can make `ITP` take 1 iteration more than ``n_max = 34``, in the published
    form as well as in the robust form."""
    # --- arrange ----------------------
    f, _ = _PAPER_TABLE_1[name]

    # --- act --------------------------
    result = ITP(n_slack=0, is_robust=is_robust).solve(f, -1.0, 1.0, xtol=_XTOL, max_fevals=100)

    # --- assert -----------------------
    assert result.n_fevals - 2 == _N_BISECTION + 1


# ==================================================================================================
#  The steps
# ==================================================================================================
@pytest.mark.parametrize("is_robust", [True, False])
def test_a_root_at_the_midpoint_is_found_in_1_iteration(is_robust):
    """On a line through 0 over ``[-1, 1]``, the interpolation lands on the midpoint, which is the root."""
    # --- act --------------------------
    result = ITP(n_slack=0, is_robust=is_robust).solve(lambda x: x, -1.0, 1.0, xtol=_XTOL, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.0, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `ITP` converges within ``xtol`` of the
    root."""
    # --- act --------------------------
    result = ITP(n_slack=4, is_robust=True).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


def test_a_negative_n_slack_is_rejected():
    """A negative ``n_slack`` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="-1"):
        ITP(n_slack=-1, is_robust=True)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`ITP` has name ``itp`` and version 1, and its flop count includes the logarithm that sets ``n_bisection``."""
    # --- act --------------------------
    result = ITP(n_slack=4, is_robust=True).solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=40)

    # --- assert -----------------------
    assert (ITP.name, ITP.version) == ("itp", 1)
    assert result.flop_counts.LOG2 == 1
