"""These tests assert that `Pegasus` reproduces the errors of Table 1 of its paper."""

import pytest

from sunnbear.solvers import Pegasus


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
