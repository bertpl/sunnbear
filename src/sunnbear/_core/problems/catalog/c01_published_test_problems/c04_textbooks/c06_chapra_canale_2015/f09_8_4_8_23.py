"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.4, (8.23), Fig. 8.6`` in the survey of published test problems. The
survey gives this function as 1 expression that the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot translate: a variable named `f`, and a parameter defined
by a formula of the other parameters, `Re = rho*V*D/mu`. A person therefore writes this module, and a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ChapraCanale201584823(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``f = 0.25/(log10(eps/(3.7*D) + 2.51/(Re*sqrt(f))))^2``, with the
    parameters `Re = rho*V*D/mu`; `rho = 1.23` kg/m^3, `mu = 1.79E-5` N s/m^2, `D = 0.005` m, `V = 40` m/s, `eps =
    1.5E-6` m (the book's 0.0015 mm), so `Re = 13743` (§8.4); the formula's interval is ``[0.008, 0.08]``.

    (8.21) solved for its first ``f``; the book prints ``log``, base 10. Fixed-point iteration from any guess in the
    interval reaches an error below 0.008% in 6 or fewer iterations.

    The formula's ``x`` is the source's friction factor ``f``, and the formula is the difference form ``f -
    0.25/(...)^2`` of the fixed-point equation, with the values of Section 8.4's example: ``eps = 1.5E-6``, and ``Re =
    rho*V*D/mu`` computed as the book's MATLAB code computes it.
    """

    number = (1, 4, 6, 9)
    name = "§8.4, (8.23)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="§8.4, (8.23), Fig. 8.6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.072 * c
        # the formula is the difference form x - 0.25/(...)^2 of the fixed-point equation (8.23), with the values
        # of Section 8.4's example
        diameter, eps = 0.005, 1.5e-6
        reynolds = 1.23 * 40.0 * diameter / 1.79e-5
        return x - 0.25 / math.log10(eps / (3.7 * diameter) + 2.51 / (reynolds * math.sqrt(x))) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.008, 0.08)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.0296, c=0.0, expected=0.0007179248847414975),
        FormulaTestCase.value(params={}, x=0.0296, c=0.25, expected=-0.021449364335113793),
        FormulaTestCase.interval_bounds(params={}, expected=(0.008, 0.08)),
    )
