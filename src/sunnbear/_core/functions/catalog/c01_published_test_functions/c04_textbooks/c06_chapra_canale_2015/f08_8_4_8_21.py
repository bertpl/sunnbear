"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.4, (8.21), Fig. 8.5; Prob. 8.13`` in the survey of published test
problems. The survey gives this function as 1 expression that the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot translate: a parameter defined by a formula of the other
parameters, `Re = rho*V*D/mu`. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale201584821(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``1/sqrt(f) + 2.0*log10(eps/(3.7*D) + 2.51/(Re*sqrt(f)))``, with the
    parameters `Re = rho*V*D/mu`; `rho = 1.23` kg/m^3, `mu = 1.79E-5` N s/m^2, `D = 0.005` m, `V = 40` m/s, `eps =
    1.5E-6` m (the book's 0.0015 mm), so `Re = 13743` (§8.4, Prob. 8.13(a)); `eps = 4.5E-5` m (the book's 0.045 mm,
    Prob. 8.13(b)); the formula's interval is ``[0.008, 0.08]``.

    Unknown ``f``, the friction factor of turbulent flow in a pipe of roughness ``eps`` and diameter ``D``. The book
    prints ``log``, a base-10 log as its MATLAB code shows; Prob. 8.13 prints ``1/sqrt(f) = -2.0*log(...)``. Root
    ``0.0289678``. Bisection takes 22 iterations and false position 26. Newton converges from 0.008 in 6 iterations,
    diverges from 0.08 (it converges only from below about 0.066), and converges in 3 from the Swamee–Jain estimate
    (8.22), 0.029031. MATLAB's ``fzero`` fails from 0.008, where it meets a complex value, and works from above about
    0.016. Prob. 8.13 suggests the Blasius estimate ``0.316/Re^0.25`` as the initial guess.

    The formula's ``x`` is the source's friction factor ``f``. The formula computes ``Re = rho*V*D/mu`` unrounded, as
    the book's MATLAB code does; the book's text rounds ``Re`` to 13743.
    """

    number = (1, 4, 6, 8)
    name = "§8.4, (8.21)"
    param_names = ("eps",)
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="§8.4, (8.21), Fig. 8.5; Prob. 8.13",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, eps: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.072 * c
        # compute the Reynolds number Re = rho*V*D/mu as the book's MATLAB code computes it
        diameter = 0.005
        reynolds = 1.23 * 40.0 * diameter / 1.79e-5
        return 1.0 / math.sqrt(x) + 2.0 * math.log10(eps / (3.7 * diameter) + 2.51 / (reynolds * math.sqrt(x)))

    def interval_bounds(self, eps: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.008, 0.08)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("eps",), rows=((1.5e-06,), (4.5e-05,))),)

    test_cases = (
        FormulaTestCase.value(params={"eps": 1.5e-06}, x=0.0296, c=0.0, expected=-0.07179608309477187),
        FormulaTestCase.value(params={"eps": 1.5e-06}, x=0.0296, c=0.25, expected=3.7840607685120067),
        FormulaTestCase.value(params={"eps": 4.5e-05}, x=0.0296, c=0.0, expected=0.899026613174279),
        FormulaTestCase.interval_bounds(params={"eps": 1.5e-06}, expected=(0.008, 0.08)),
    )
