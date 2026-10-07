"""These tests assert that `Pegasus` scales down the value of a bound that the interval keeps twice in a row, by the
factor ``f_previous / (f_previous + f_new)``, which ends regula falsi's stall."""

import pytest

from sunnbear.solvers import Pegasus, RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


# ==================================================================================================
#  The modified step
# ==================================================================================================
@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first chord lands on the root, so `Pegasus` converges after the 2 bound evaluations
    and 1 iterate."""
    # --- act --------------------------
    result = Pegasus().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_the_first_2_steps_are_regula_falsi_and_later_steps_scale_the_retained_f():
    """On the convex cubic, Pegasus starts as regula falsi, then scales the value of the bound that it keeps again,
    each time by the factor ``f_previous / (f_previous + f_new)`` of the 2 most recent iterates."""
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = Pegasus().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, f3), (x4, _) = history[2:6]
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    assert x2 == (x1 * fb - b * f1) / (fb - f1)
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is scaled.
    assert f2 < 0.0
    scaled_fb = (f1 / (f1 + f2)) * fb
    assert x3 == (x2 * scaled_fb - b * f2) / (scaled_fb - f2)
    # f3 < 0 too: the scaled value is scaled again, by the factor of x2 and x3.
    assert f3 < 0.0
    scaled_fb = (f2 / (f2 + f3)) * scaled_fb
    assert x4 == (x3 * scaled_fb - b * f3) / (scaled_fb - f3)


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # The 2 functions cover both interval orientations.
def test_a_convex_function_converges_where_regula_falsi_stalls(f):
    """On `cubic` in both interval orientations, regula falsi exhausts its budget, while Pegasus converges well
    within it."""
    # --- act --------------------------
    regula_falsi_result = RegulaFalsi().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)
    pegasus_result = Pegasus().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)

    # --- assert -----------------------
    assert regula_falsi_result.status is SolveStatus.MAX_FEVALS
    assert pegasus_result.status is SolveStatus.CONVERGED
    assert abs(pegasus_result.x - CUBIC_ROOT) <= 1e-9
    assert pegasus_result.n_fevals <= 15


# ==================================================================================================
#  Table 1 of Dowell and Jarratt (1972)
# ==================================================================================================
def test_the_errors_of_table_1_of_the_dowell_jarratt_paper_are_reproduced():
    """The iterates of `Pegasus` on ``x^3 + 1``, mirrored, have the errors in Table 1 of Dowell and Jarratt (1972).

    The paper starts from x_0 = 0 and x_1 = -2, so its newest starting point is the lower one, while `Pegasus` takes
    the upper bound as its newest starting point. The test therefore solves the mirrored function ``1 - x^3`` over
    ``[0, 2]``, whose iterates are the paper's with their signs flipped, and negates each error.

    The table lists the error ``x_i + 1`` of the iterates ``i = 2`` to 9, each rounded to 3 significant digits. That
    rounding changes a value by at most 0.5 %, so the test compares each error within 0.5 %.

    The test leaves out the table's last 2 rows, with errors below 1e-9: they differ from the float64 iterates by about
    1 % for x_8 and in sign for x_9, presumably because of the precision of the paper's computer.
    """
    # --- arrange ----------------------
    dowell_jarratt_table_1_errors = [0.750, 0.534, 0.232, -0.682e-2, 0.184e-2, 0.125e-4]

    # --- act --------------------------
    result = Pegasus().solve(lambda x: 1.0 - x**3, 0.0, 2.0, xtol=1e-15, max_fevals=20, history_enabled=True)

    # --- assert -----------------------
    # The history starts with the 2 starting points, the mirrored x_0 and x_1, so ``evaluated_x_values[2:8]`` holds
    # the mirrored x_2 to x_7; the mirrored root is 1.
    errors = [-(x - 1.0) for x in result.evaluated_x_values[2:8]]
    assert errors == pytest.approx(dowell_jarratt_table_1_errors, rel=5e-3)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Pegasus` is named ``pegasus``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Pegasus().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Pegasus.name, Pegasus.version) == ("pegasus", 1)
    assert result.flop_counts.total_count() > 0
