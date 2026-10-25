"""This module holds a formula of Steffen et al. (2025).

The formula comes from the row with the key ``(8)`` in the survey of published test problems. The survey gives this
function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: an expression with a function ``alpha`` that the row's parameters define. A person therefore writes this
module, and a change of the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class SteffenEtAl20258(Formula):
    """This formula comes from Steffen et al. (2025).

    The survey writes the source's function as ``(V/b)^3 - (1 - lambda + Tr/(Gamma*Pr))*(V/b)^2 + (sigma - lambda -
    lambda*Tr/(Gamma*Pr) + Lambda*alpha(omega, Tr)/(Gamma^2*Pr))*(V/b) - (sigma + sigma*Tr/(Gamma*Pr) +
    Lambda*alpha(omega, Tr)/(Gamma^2*Pr))``, with the parameters ``lambda = 2, sigma = -1, Lambda = 0.45724, Gamma =
    0.07780``; ``alpha(omega, Tr) = (1 + (0.37464 + 1.54226*omega - 0.26992*omega^2)*(1 - sqrt(Tr)))^2`` (Eq. (9));
    ``omega = 0.200, Tr = 0.85, Pr = 0.45``; the formula's interval is ``[14, 17]``.

    The formula's parameter ``lambda_`` is the source's ``lambda``, renamed because ``lambda`` is a Python keyword.

    The variable is ``V/b``, the volume over the covolume parameter. It has 3 roots (Fig. 5); the interval holds the
    vapor-phase one. Tolerance ``1E-10``; printed root ``15.0676609061``. That root lies within ``6.5E-9`` of the root
    at full-precision ``Lambda`` and ``Gamma``, ``15.0676608996``; with the printed ``0.45724`` and ``0.07780``, the
    root on ``[14, 17]`` is about ``15.0670``.
    """

    number = (1, 1, 11, 2)
    name = "(8)"
    param_names = ("lambda_", "sigma", "Lambda", "Gamma", "omega", "Tr", "Pr")
    source = FormulaSource(
        reference=(
            "Steffen, V., Della Pasqua, C. C., de Oliveira, M. S., da Silva, E. A. (2025). Halving "
            "interval guaranteed for Dekker and Brent root finding methods. Examples and "
            "Counterexamples 7, 100173. https://doi.org/10.1016/j.exco.2024.100173."
        ),
        location="(8)",
    )

    @staticmethod
    def parametrized_fun(
        x: float,
        c: float,
        lambda_: float,
        sigma: float,
        Lambda: float,
        Gamma: float,
        omega: float,
        Tr: float,
        Pr: float,
    ) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        alpha = (1 + (0.37464 + 1.54226 * omega - 0.26992 * omega**2) * (1 - math.sqrt(Tr))) ** 2
        return (
            x**3
            - (1 - lambda_ + Tr / (Gamma * Pr)) * x**2
            + (sigma - lambda_ - lambda_ * Tr / (Gamma * Pr) + Lambda * alpha / (Gamma**2 * Pr)) * x
            - (sigma + sigma * Tr / (Gamma * Pr) + Lambda * alpha / (Gamma**2 * Pr))
        )

    def interval_bounds(
        self, lambda_: float, sigma: float, Lambda: float, Gamma: float, omega: float, Tr: float, Pr: float
    ) -> tuple[float, float]:
        """Return the formula's interval."""
        return (14.0, 17.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("lambda_", "sigma", "Lambda", "Gamma", "omega", "Tr", "Pr"),
                rows=((2.0, -1.0, 0.45724, 0.0778, 0.2, 0.85, 0.45),),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={
                "lambda_": 2.0,
                "sigma": -1.0,
                "Lambda": 0.45724,
                "Gamma": 0.0778,
                "omega": 0.2,
                "Tr": 0.85,
                "Pr": 0.45,
            },
            x=14.9,
            c=0.0,
            expected=-18.42303100506896,
        ),
        FormulaTestCase.value(
            params={
                "lambda_": 2.0,
                "sigma": -1.0,
                "Lambda": 0.45724,
                "Gamma": 0.0778,
                "omega": 0.2,
                "Tr": 0.85,
                "Pr": 0.45,
            },
            x=14.9,
            c=0.25,
            expected=-86.8301765128466,
        ),
        FormulaTestCase.interval_bounds(
            params={
                "lambda_": 2.0,
                "sigma": -1.0,
                "Lambda": 0.45724,
                "Gamma": 0.0778,
                "omega": 0.2,
                "Tr": 0.85,
                "Pr": 0.45,
            },
            expected=(14.0, 17.0),
        ),
    )
