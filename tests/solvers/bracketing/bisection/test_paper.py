"""These tests assert that `Bisection` reproduces Table 2.1 of Atkinson's textbook."""

from decimal import ROUND_HALF_UP, Decimal

from sunnbear.solvers import Bisection


def test_the_midpoints_of_table_2_1_of_atkinson_are_reproduced():
    """On ``x^6 - x - 1`` over ``[1, 2]``, with Atkinson's ``epsilon = 0.00005`` as ``xtol``, `Bisection` evaluates
    the midpoints ``c_1`` to ``c_14`` of Table 2.1 of Atkinson (1989), and returns ``c_15``.

    The table prints each midpoint and its function value rounded to at most 5 decimals, and rounds a tie up: it
    prints ``c_6 = 1.140625`` as 1.14063.

    Atkinson's algorithm, like `Bisection`, stops once ``c_15`` lies within ``epsilon`` of both bounds of the current
    interval, and accepts ``c_15`` without evaluating it. The table's ``f(c_15) = 0.00016`` is ``f`` evaluated at the
    rounded value 1.13474, not at ``c_15``, so the test does not compare the table's ``f(c_15)``.
    """
    # --- arrange ----------------------
    printed_rows_c_1_to_c_14 = [
        ("1.5", "8.89063"),
        ("1.25", "1.56470"),
        ("1.125", "-0.09771"),
        ("1.1875", "0.61665"),
        ("1.15625", "0.23327"),
        ("1.14063", "0.06158"),
        ("1.13281", "-0.01958"),
        ("1.13672", "0.02062"),
        ("1.13477", "0.00043"),
        ("1.13379", "-0.00960"),
        ("1.13428", "-0.00459"),
        ("1.13452", "-0.00208"),
        ("1.13464", "-0.00083"),
        ("1.13470", "-0.00020"),
    ]
    printed_c_15 = Decimal("1.13474")

    # --- act --------------------------
    result = Bisection().solve(lambda x: x**6 - x - 1.0, 1.0, 2.0, xtol=0.00005, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    # The history starts with the 2 interval bounds, so ``history[2:]`` holds c_1 to c_14 and their function values.
    assert len(result.history) == 2 + len(printed_rows_c_1_to_c_14)
    for (c, fc), (printed_c, printed_fc) in zip(result.history[2:], printed_rows_c_1_to_c_14, strict=True):
        assert Decimal(c).quantize(Decimal(printed_c), rounding=ROUND_HALF_UP) == Decimal(printed_c)
        assert Decimal(fc).quantize(Decimal(printed_fc), rounding=ROUND_HALF_UP) == Decimal(printed_fc)
    assert Decimal(result.x).quantize(printed_c_15, rounding=ROUND_HALF_UP) == printed_c_15
