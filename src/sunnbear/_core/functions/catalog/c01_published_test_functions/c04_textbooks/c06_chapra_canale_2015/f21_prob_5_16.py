"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.16`` in the survey of published test problems. The survey gives
this function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: variables that depend on the unknown `y`, `B = 3 + y` and `Ac = 3*y + y^2/2`, which the row lists among its
parameters. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ChapraCanale2015Prob516(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``1 - Q^2/(g*Ac^3)*B``, with the parameters `Q = 20` m^3/s, `g = 9.81`
    m/s^2, `B = 3 + y`, `Ac = 3*y + y^2/2`; the formula's interval is ``[0.5, 2.5]``.

    Unknown ``y``, the critical depth (m); ``B`` is the width at the surface and ``Ac`` the cross-sectional area.
    Graphically, and by bisection and false position to ``es = 1%`` or at most 10 iterations.

    The formula's ``x`` is the source's depth ``y``.
    """

    number = (1, 4, 6, 21)
    name = "Prob. 5.16"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.16",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        surface_width = 3.0 + x
        area = 3.0 * x + x**2 / 2.0
        return 1.0 - 20.0**2 / (9.81 * area**3) * surface_width

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 2.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.1, c=0.0, expected=-1.8074480329135572),
        FormulaTestCase.value(params={}, x=1.1, c=0.25, expected=-17.910278020703927),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 2.5)),
    )
