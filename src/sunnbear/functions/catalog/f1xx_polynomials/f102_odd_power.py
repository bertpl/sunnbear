"""f102 — odd power ``x^p1 - c``: a difficulty knob."""

from sunnbear.functions import Formula, ParamRecipe


class F102_OddPower(Formula):
    """Difficulty-knob polynomial: higher odd powers flatten the root at ``c = 0``.

    Higher powers turn a benign polynomial into a derivative-zero stress case.
    Implemented without numba (``jit = False``) to exercise the framework's
    plain-Python path.
    """

    number = 102
    name = "odd_power"
    jit = False

    @staticmethod
    def parametrized_fun(x: float, c: float, p1: float) -> float:
        """Evaluate ``x^p1 - c``."""
        return x**p1 - c

    def bracket(self, p1: float) -> tuple[float, float]:
        """Fixed bracket, wide enough for the calibrated c-range."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Sweep the power over the odd integers."""
        return (ParamRecipe.linear("p1", 1.0, 7.0, step=2.0),)

    def is_param_tuple_valid(self, p1: float) -> bool:
        """Require an odd integer power (even powers break the sign change across the bracket)."""
        return p1 == int(p1) and int(p1) % 2 == 1
