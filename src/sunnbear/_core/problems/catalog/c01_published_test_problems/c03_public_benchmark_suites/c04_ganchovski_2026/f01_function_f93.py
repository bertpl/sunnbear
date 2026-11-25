"""This module holds a formula of Ganchovski (2026).

The formula comes from the rows with the keys ``f93``, ``f94``, ``f95``, ``f96``, ``f97``, ``f98`` and ``f99`` in the
survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Ganchovski2026FunctionF93(Formula):
    """This formula comes from Ganchovski (2026).

    The source prints 7 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 7 functions become 1 function, ``x^n - 0.001``:

    - f93, with ``n = 5``: ``x^5 - 0.001``; the formula's interval is ``[-10, 10]``
    - f94, with ``n = 7``: ``x^7 - 0.001``; the formula's interval is ``[-10, 10]``
    - f95, with ``n = 9``: ``x^9 - 0.001``; the formula's interval is ``[-10, 10]``
    - f96, with ``n = 11``: ``x^11 - 0.001``; the formula's interval is ``[-10, 10]``
    - f97, with ``n = 13``: ``x^13 - 0.001``; the formula's interval is ``[-10, 10]``
    - f98, with ``n = 15``: ``x^15 - 0.001``; the formula's interval is ``[-10, 10]``
    - f99, with ``n = 17``: ``x^17 - 0.001``; the formula's interval is ``[-10, 10]``
    """

    number = (1, 3, 4, 1)
    name = "Function f93"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "f93, f94, f95, f96, f97, f98 and f99"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{\param{n}} - 0.001",
        interval="[-10, 10]",
        summary=(
            r"An odd power minus 0.001, nearly flat on a band around $\x = 10 \c$ that ends at the root, and steep more"
            r" than 1 away from $\x = 10 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**n - 0.001

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=((5.0,), (7.0,), (9.0,), (11.0,), (13.0,), (15.0,), (17.0,)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 5.0}, x=-4.0, c=0.0, expected=-1024.001),
        FormulaTestCase.value(params={"n": 5.0}, x=-4.0, c=0.5, expected=-59049.001),
        FormulaTestCase.value(params={"n": 7.0}, x=-4.0, c=0.0, expected=-16384.001),
        FormulaTestCase.value(params={"n": 9.0}, x=-4.0, c=0.0, expected=-262144.001),
        FormulaTestCase.value(params={"n": 11.0}, x=-4.0, c=0.0, expected=-4194304.001),
        FormulaTestCase.value(params={"n": 13.0}, x=-4.0, c=0.0, expected=-67108864.001),
        FormulaTestCase.value(params={"n": 15.0}, x=-4.0, c=0.0, expected=-1073741824.001),
        FormulaTestCase.value(params={"n": 17.0}, x=-4.0, c=0.0, expected=-17179869184.001),
        FormulaTestCase.interval_bounds(params={"n": 5.0}, expected=(-10.0, 10.0)),
    )
