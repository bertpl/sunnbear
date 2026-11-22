"""This module holds a formula of Steffen et al. (2025).

The formula comes from the row with the key ``(8)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


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
    params = (
        FormulaParam("lambda_", latex_symbol=r"\lambda"),
        FormulaParam("sigma", latex_symbol=r"\sigma"),
        FormulaParam("Lambda", latex_symbol=r"\Lambda"),
        FormulaParam("Gamma", latex_symbol=r"\Gamma"),
        FormulaParam("omega", latex_symbol=r"\omega"),
        FormulaParam("Tr", latex_symbol="T_r"),
        FormulaParam("Pr", latex_symbol="P_r"),
    )
    location_in_publication = "Eq. (8)"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 3 \c"),
            (
                r"\fn{\alpha}(\param{omega}, \param{Tr})",
                r"\left(1 + (0.37464 + 1.54226 \param{omega} - 0.26992 \param{omega}^2)"
                r"\left(1 - \sqrt{\param{Tr}}\right)\right)^2",
            ),
        ),
        expression=(
            r"\tmp{u}^3 - \left(1 - \param{lambda_} + \frac{\param{Tr}}{\param{Gamma} \param{Pr}}\right) \tmp{u}^2 "
            r"+ \left(\param{sigma} - \param{lambda_} - \frac{\param{lambda_} \param{Tr}}{\param{Gamma} \param{Pr}} "
            r"+ \frac{\param{Lambda} \fn{\alpha}(\param{omega}, \param{Tr})}{\param{Gamma}^2 \param{Pr}}\right) "
            r"\tmp{u} "
            r"- \left(\param{sigma} + \frac{\param{sigma} \param{Tr}}{\param{Gamma} \param{Pr}} "
            r"+ \frac{\param{Lambda} \fn{\alpha}(\param{omega}, \param{Tr})}{\param{Gamma}^2 \param{Pr}}\right)"
        ),
        interval="[14, 17]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

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
                summary="The published parameter values.",
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
