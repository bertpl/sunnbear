"""f101 — cubic ``x^3 - p1*x - c``."""

from sunnbear.functions import Formula, FormulaTestCase, ParamRecipe


class F101_Cubic(Formula):
    """Benign cubic; ``p1`` tilts the central slope, ``c`` shifts the root."""

    number = 101
    name = "cubic"
    param_names = ("p1",)

    @staticmethod
    def parametrized_fun(x: float, c: float, p1: float) -> float:
        """Evaluate ``x^3 - p1*x - c``."""
        return x * x * x - p1 * x - c

    def bracket(self, p1: float) -> tuple[float, float]:
        """Fixed bracket, wide enough for the calibrated c-range."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Sweep the slope knob linearly."""
        return (ParamRecipe.decimal("p1", 0.0, 1.0, step=0.2),)

    cases = (
        FormulaTestCase.value(params=(0.0,), x=0.0, c=0.0, expected=0.0),  # root at the origin
        FormulaTestCase.value(params=(1.0,), x=2.0, c=1.0, expected=5.0),  # 8 - 2 - 1, exercises c
        FormulaTestCase.bracket(params=(0.0,), expected=(-2.0, 2.0)),
    )
