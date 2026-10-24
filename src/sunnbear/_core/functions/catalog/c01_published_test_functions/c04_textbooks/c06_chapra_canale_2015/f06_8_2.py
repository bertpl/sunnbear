"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.2, (8.14)`` in the survey of published test problems. The survey gives
this function as 1 expression with a change of its variable to the pH, as `f(10^-pH)`, which the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot apply, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale201582(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``K1/(10^6*H)*KH*pCO2 + 2*K2*K1/(10^6*H^2)*KH*pCO2 + Kw/H - H``, with the
    parameters `KH = 10^-1.46`, `K1 = 10^-6.3`, `K2 = 10^-10.3`, `Kw = 10^-14`; `pCO2 = 315, 375` ppm (1958, 2003); the
    survey's interval, in the source's variable, is `[1E-12, 1E-2]` (the pH from 2 to 12).

    Unknown ``H``, the hydrogen-ion concentration ``[H+]``, which gives the pH ``-log10(H)`` of rainwater; the book
    derives (8.14) from 5 equilibrium equations, and calls it a cubic in ``[H+]``. Bisection on the pH, from the initial
    guesses 2 and 12, which the interval gives as values of ``H``: 11 iterations, for an absolute error of 0.005, give
    5.6279 for 1958, and 35 give 5.6304; 2003 gives 5.59.

    The formula's variable is the pH, as ``f(10^-pH)`` on ``[2, 12]``: the book prints the charge balance (8.14) in
    ``H`` and bisects on the pH from 2 to 12. The constants ``KH``, ``K1``, ``K2`` and ``Kw`` are fixed; ``pCO2`` is the
    formula's parameter.
    """

    number = (1, 4, 6, 6)
    name = "§8.2"
    param_names = ("pCO2",)
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="§8.2, (8.14)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, pCO2: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        # the formula's variable is the pH; the source's function is in H = 10^-pH
        h = 10.0**-x
        k_h, k_1, k_2, k_w = 10.0**-1.46, 10.0**-6.3, 10.0**-10.3, 10.0**-14
        return k_1 / (1e6 * h) * k_h * pCO2 + 2 * k_2 * k_1 / (1e6 * h**2) * k_h * pCO2 + k_w / h - h

    def interval_bounds(self, pCO2: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 12.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("pCO2",), rows=((315.0,), (375.0,))),)

    test_cases = (
        FormulaTestCase.value(params={"pCO2": 315.0}, x=5.0, c=0.0, expected=-9.45158725187333e-06),
        FormulaTestCase.value(params={"pCO2": 315.0}, x=5.0, c=0.25, expected=-0.003162275925952294),
        FormulaTestCase.value(params={"pCO2": 375.0}, x=5.0, c=0.0, expected=-9.34731815699206e-06),
        FormulaTestCase.interval_bounds(params={"pCO2": 315.0}, expected=(2.0, 12.0)),
    )
