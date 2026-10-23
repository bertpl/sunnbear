"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``A.2`` in the survey of published test problems. The survey gives this
function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: an expression with noise of a stated distribution. A person therefore writes this module, and a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import normal_noise


class KumarSrivastav2026A2(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``x - exp(-x) + eps``, with the parameters ``eps ~ N(0, sigma^2)``, drawn
    independently at each evaluation; ``sigma = 10^-3``; the formula's interval is ``[0, 1]``.

    A formula is a pure function of x, so ``eps`` is ``sigma`` times ``normal_noise(x)``, a value that depends only on x
    and is distributed as a standard normal random draw.

    Evaluations at the same x give the same value, and evaluations at different x-values give values that are as
    independent as random draws.

    The article writes it as ``g(x) + eps`` with ``g(x) = x - e^-x``, and states the root ``0.5671432904``. Table 8's
    caption writes the noise as ``N(0, 10^-3)``, but gives its standard deviation as ``10^-3``, as the text does.
    """

    number = (1, 2, 19, 6)
    name = "A.2"
    param_names = ("sigma",)
    source = FormulaSource(
        reference=(
            "Kumar, D., Srivastav, S. K. (2026). A randomized bracketing method for derivative-free "
            "root finding with uniform spacing contraction. Research Square preprint. "
            "https://doi.org/10.21203/rs.3.rs-10070193/v1. The article's Data Availability statement "
            "offers the authors' scripts from the corresponding author on request."
        ),
        location="A.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, sigma: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x - math.exp(-x) + sigma * normal_noise(x)

    def interval_bounds(self, sigma: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("sigma",), rows=((0.001,),)),)

    cases = (
        FormulaTestCase.value(params={"sigma": 0.001}, x=0.3, c=0.0, expected=-0.44033624226830675),
        FormulaTestCase.value(params={"sigma": 0.001}, x=0.3, c=0.25, expected=-0.9047881711348748),
        FormulaTestCase.interval_bounds(params={"sigma": 0.001}, expected=(0.0, 1.0)),
    )
