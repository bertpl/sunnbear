"""This module holds a formula of Alefeld, Potra (1992).

The formula comes from the rows with the keys ``1`` and ``4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaParam, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class AlefeldPotra19921(Formula):
    """This formula comes from Alefeld, Potra (1992).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``x^3 - k``:

    - 1, with ``k = 1``: ``x^3 - 1``; the formula's interval is ``[0.5, 1.5]``
    - 4, with ``k = -1``: ``x^3 + 1``; the formula's interval is ``[-1.8, 0]``
    """

    number = (1, 2, 3, 1)
    name = "1"
    params = (
        FormulaParam("k"),
        FormulaParam("a"),
        FormulaParam("b"),
        FormulaParam("c_scale"),
    )
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A. (1992). Some efficient methods for enclosing simple zeros of "
            "nonlinear equations. BIT 32(2), 334–344. https://doi.org/10.1007/bf01994885."
        ),
        location="1, 4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 - k

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("k", "a", "b", "c_scale"), rows=((1.0, 0.5, 1.5, 1.0), (-1.0, -1.8, 0.0, 1.8))),)

    test_cases = (
        FormulaTestCase.value(
            params={"k": 1.0, "a": 0.5, "b": 1.5, "c_scale": 1.0}, x=0.8, c=0.0, expected=-0.48799999999999993
        ),
        FormulaTestCase.value(params={"k": 1.0, "a": 0.5, "b": 1.5, "c_scale": 1.0}, x=0.8, c=0.25, expected=-0.833625),
        FormulaTestCase.value(
            params={"k": -1.0, "a": -1.8, "b": 0.0, "c_scale": 1.8}, x=-1.26, c=0.0, expected=-1.000376
        ),
        FormulaTestCase.interval_bounds(params={"k": 1.0, "a": 0.5, "b": 1.5, "c_scale": 1.0}, expected=(0.5, 1.5)),
        FormulaTestCase.interval_bounds(params={"k": -1.0, "a": -1.8, "b": 0.0, "c_scale": 1.8}, expected=(-1.8, 0.0)),
    )
