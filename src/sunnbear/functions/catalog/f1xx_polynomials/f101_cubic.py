"""f101 — cubic ``x^3 - p1*x - c``."""

from sunnbear.functions import Formula, ParamRecipe, XCFun


class F101_Cubic(Formula):
    """Benign cubic; ``p1`` tilts the central slope, ``c`` shifts the root."""

    number = 101
    name = "cubic"
    param_names = ("p1",)

    def make_fun(self, p1: float) -> XCFun:
        """Build ``x^3 - p1*x - c``."""

        def f(x: float, c: float) -> float:
            return x * x * x - p1 * x - c

        return f

    def bracket(self, p1: float) -> tuple[float, float]:
        """Fixed bracket, wide enough for the calibrated c-range."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Sweep the slope knob linearly."""
        return (ParamRecipe.linear("p1", 0.0, 1.0, step=0.2),)
