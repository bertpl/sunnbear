"""This module holds a formula of Roots.jl (2026).

The formula comes from the rows with the keys ``func2`` and ``f3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class RootsJl2026Func2(Formula):
    """This formula comes from Roots.jl (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - func2: ``exp(x) - x^4``; the formula's interval is `[-5.0, 20.0]` (`find_zeros`)
    - f3: ``exp(x) - x^4``; the formula's interval is ``[5.0, 20.0]``

    func2: The source's 11 starting points are evenly spaced from `5.0` to `20.0`.

    f3: The source's starting point is `x0 = 7.0`.
    """

    number = (1, 3, 6, 1)
    name = "func2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Roots.jl v3.0.11, the test folder https://github.com/JuliaMath/Roots.jl/tree/v3.0.11/test,"
            " MIT license. The functions of the rows are in 2 files:\n"
            "- `test/test_derivative_free.jl`, "
            "https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/test_derivative_free.jl\n"
            "- `test/runbenchmarks.jl`, "
            "https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/runbenchmarks.jl\n"
            "\n"
            "The files cite 1 source: the comment `## multiplicity: "
            "http://ir.igsnrr.ac.cn/bitstream/311030/8840/1/%E4%BE%AF%E9%BA%9F%E7%A7%91(SCI)2.pdf` "
            "stands above `func13` in `test_derivative_free.jl`. The URL gives no title; its file name "
            "decodes to `侯麟科(SCI)2.pdf`.\n"
            "\n"
            "The paper at the URL is Li et al. (2010): Li, X., Mu, C., Ma, J., Hou, L. (2011). "
            "Fifth-order iterative method for finding multiple roots of nonlinear equations. Numerical "
            "Algorithms 57(3), 389–398, published online in 2010. "
            "https://doi.org/10.1007/s11075-010-9434-5. Its rows are in `2010_li_multiple_roots`."
        ),
        location="test_derivative_free.jl, func2; runbenchmarks.jl, f3",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}} - \tmp{u}^{4}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - x**4

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-5.0, 20.0, 25.0), (5.0, 20.0, 15.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -5.0, "b": 20.0, "c_scale": 25.0}, x=2.5, c=0.0, expected=-26.880006039296525
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 20.0, "c_scale": 25.0}, x=2.5, c=0.25, expected=-197.730388504144
        ),
        FormulaTestCase.value(params={"a": 5.0, "b": 20.0, "c_scale": 15.0}, x=9.5, c=0.0, expected=5214.664329661872),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 20.0, "c_scale": 25.0}, expected=(-5.0, 20.0)),
        FormulaTestCase.interval_bounds(params={"a": 5.0, "b": 20.0, "c_scale": 15.0}, expected=(5.0, 20.0)),
    )
