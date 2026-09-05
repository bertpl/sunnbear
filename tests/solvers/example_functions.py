"""Example functions shared by the solver tests: a plain cubic and a calibrated catalog function."""

from sunnbear.functions import FormulaRegistry, TestFunction


def cube_minus_two(x: float) -> float:
    return x**3 - 2.0


def calibrated_cubic() -> TestFunction:
    """Return catalog formula f101 with ``p1 = 0.2``, calibrated on ``c`` in ``[-5, 5]``."""
    return FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0)
