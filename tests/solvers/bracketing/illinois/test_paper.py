"""These tests assert that `Illinois` reproduces the errors of Table 1 of its paper."""

import math

import pytest

from sunnbear.solvers import Illinois


def test_the_errors_of_table_1_of_the_dowell_jarratt_paper_are_reproduced():
    """The iterates of `Illinois` on ``sin(x) - 0.5`` have the errors in Table 1 of Dowell and Jarratt (1971).

    The test starts `Illinois` from 0 and 1.5, the paper's x_0 and x_1. The table lists the error ``x_i - pi/6`` of
    the iterates ``i = 2`` to 10, each rounded to 3 significant digits. That rounding changes a value by at most
    0.5 %, so the test compares each error within 0.5 %.

    The table's error for x_10, below 0.5e-18, is smaller than the gap between adjacent float64 values near ``pi/6``,
    so the test leaves that error out.
    """
    # --- arrange ----------------------
    dowell_jarratt_table_1_errors = [0.228, -0.895e-1, 0.666e-2, 0.160e-3, -0.152e-3, 0.702e-8, 0.308e-12, -0.308e-12]

    # --- act --------------------------
    result = Illinois().solve(lambda x: math.sin(x) - 0.5, 0.0, 1.5, xtol=1e-15, max_fevals=20, history_enabled=True)

    # --- assert -----------------------
    # The history starts with the 2 starting points, the paper's x_0 and x_1, so ``evaluated_x_values[2:10]`` holds
    # x_2 to x_9.
    errors = [x - math.pi / 6.0 for x in result.evaluated_x_values[2:10]]
    assert errors == pytest.approx(dowell_jarratt_table_1_errors, rel=5e-3)
