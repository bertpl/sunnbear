"""`EffectOfC` lists the ways in which a formula applies its parameter ``c``."""

from enum import StrEnum
from typing import assert_never


# ==================================================================================================
#  EffectOfC
# ==================================================================================================
class EffectOfC(StrEnum):
    """`EffectOfC` is a way in which a formula applies ``c``, as each formula declares in `Formula.effect_of_c`.

    The declaration states what the formula's code does. A formula whose ``c`` moves x may also multiply the function's
    values by a positive factor ``g(c)``, which moves no root, as in ``f(x, c) = g(c)*f(x - s*c, 0)``.
    """

    SHIFTS_X = "shifts_x"  # f(x, c) = f(x - s*c, 0), for a constant s
    SHIFTS_Y = "shifts_y"  # f(x, c) = f(x, 0) + s*c, for a constant s
    SCALES_X = "scales_x"  # f(x, c) = f(x*k(c), 0), for a function k of c alone

    @property
    def sentence(self) -> str:
        """Return the way of applying ``c`` as a sentence for a reader.

        The sentence names the way and gives no amount, such as how far ``c`` shifts the function.
        """
        match self:
            case EffectOfC.SHIFTS_X:
                return "Shifts the function along the x-axis."
            case EffectOfC.SHIFTS_Y:
                return "Shifts the function along the y-axis."
            case EffectOfC.SCALES_X:
                return "Scales the function along the x-axis."
            case _:
                assert_never(self)
