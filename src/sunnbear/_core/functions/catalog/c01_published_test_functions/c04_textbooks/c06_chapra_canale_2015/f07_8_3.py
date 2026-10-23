"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.3, (8.19), (8.20), Fig. 8.4`` in the survey of published test problems.
The survey gives this function as 1 expression that the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot translate: a parameter given as a ratio, `q/q0 = 0.01`. A
person therefore writes this module, and a change of the formula's row in `data/literature_test_problems/sources/` needs
a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ChapraCanale201583(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``exp(-R*t/(2*L))*cos(sqrt(1/(L*C) - (R/(2*L))^2)*t) - q/q0``, with the
    parameters `L = 5` H, `C = 10^-4` F, `t = 0.05` s, `q/q0 = 0.01`; the formula's interval is ``[0, 400]``.

    Unknown ``R``, the resistance (ohm) at which the capacitor's charge decays to 1% of its initial value in 0.05 s.
    Printed with the values as (8.20), ``exp(-0.005*R)*cos(sqrt(2000 - 0.01*R^2)*0.05) - 0.01``, which needs ``2000 -
    0.01*R^2 > 0``. 21 bisection iterations give ``R = 328.1515``.

    The formula's ``x`` is the source's ``R``, and the parameters' published values are constants of the function.
    """

    number = (1, 4, 6, 7)
    name = "§8.3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="§8.3, (8.19), (8.20), Fig. 8.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 400.0 * c
        inductance, capacitance, t = 5.0, 1e-4, 0.05
        omega = math.sqrt(1.0 / (inductance * capacitance) - (x / (2.0 * inductance)) ** 2)
        return math.exp(-x * t / (2.0 * inductance)) * math.cos(omega * t) - 0.01

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 400.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=120.0, c=0.0, expected=-0.3122612452758301),
        FormulaTestCase.value(params={}, x=120.0, c=0.25, expected=-0.5669375904661977),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 400.0)),
    )
