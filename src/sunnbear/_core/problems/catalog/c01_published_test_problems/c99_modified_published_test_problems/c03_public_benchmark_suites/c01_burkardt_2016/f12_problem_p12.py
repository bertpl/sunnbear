"""This module holds formula f1.99.3.1.12, the modified version of the published formula f1.3.1.12.

A change of formula f1.3.1.12 may need a matching change of this module.
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
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedBurkardt2016ProblemP12(Formula):
    """This formula is the modified version of formula f1.3.1.12, from Burkardt (2016).

    The survey writes the source's function as ``-exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x < 1.0);
    ``0.0`` (x = 1.0); ``+exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x > 1.0), with the parameters
    ``factor = 1000.0``; the published intervals are ``[-4.0, 4.1]`` (rang); ``[0.50, 2.0]`` (starts 2 and 1).

    The source's starting points, in order, are ``2.0``, ``0.50`` and ``4.0``.

    The formula adds ``TINY_LINEAR_TERM_SLOPE*(x - 1)`` to the published function, on the published intervals; ``c``
    shifts x by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range; no way of writing the function avoids these exact zeros.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too; beyond about 0.04
    from the root, the term changes f by less than the rounding error of f.

    The modification changes what the test problem tests: with the published function, a solver may stop at any
    x-value within about 0.04 of the root, while with the term a solver must locate the root, near which f is the
    linear term.
    """

    number = (1, 99, 3, 1, 12)
    name = "Problem p12"
    params = (
        FormulaParam(
            "k",
            latex_symbol="k",
            meaning=(
                r"The scale of $\fn{g}$: for $\x \neq 1$, "
                r"$\fn{g}(\x) = \param{k} (\x - 1) e^{-1/(\x - 1)^2}$."
            ),
        ),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p12"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \param{c_scale} \c"),
            (
                r"\fn{g}(\x)",
                (
                    r"\begin{cases} -\exp\left(\ln(\param{k}) + \ln\left(\left|\x - 1\right|\right) "
                    r"- \frac{1}{(\x - 1)^2}\right) & \text{if } \x < 1 \\ 0 & \text{if } \x = 1 \\ "
                    r"\exp\left(\ln(\param{k}) + \ln\left(\left|\x - 1\right|\right) "
                    r"- \frac{1}{(\x - 1)^2}\right) & \text{otherwise} \end{cases}"
                ),
            ),
        ),
        expression=r"\fn{g}(\tmp{u}) + 2^{-918} (\tmp{u} - 1)",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function so flat at its root that the function stays below $10^{-270}$ in magnitude on a band 0.08 wide "
            'around that root, referred to in the source as "Flat Stanley".'
        ),
        notes=(
            (
                r"The term $2^{-918} (\tmp{u} - 1)$ keeps the function from being exactly 0 within about "
                r"0.04 of its root, where the published function, $\fn{g}(\tmp{u})$, underflows to 0 in "
                "float64. This changes what the test problem tests: with the published function, a solver "
                "may stop at any x-value within about 0.04 of the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*(y - 1)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if x < 1.0:
            published_value = -math.exp(math.log(k) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        elif x == 1.0:
            published_value = 0.0
        else:
            published_value = math.exp(math.log(k) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        return published_value + TINY_LINEAR_TERM_SLOPE * (x - 1.0)

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("k", "a", "b", "c_scale"),
                rows=(
                    (1000.0, -4.0, 4.1, 8.1),
                    (1000.0, 0.5, 2.0, 1.5),
                ),
                summary="The published parameter values and intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(
            params={"k": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, expected=(-4.0, 4.1)
        ),
        FormulaTestCase.value(
            params={"k": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=-1.57, c=0.25, expected=-4382.445368656935
        ),
        FormulaTestCase.value(
            params={"k": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1},
            x=1.0001,
            c=0.0,
            expected=4.512985939661577e-281,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(params={"k": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5}, expected=(0.5, 2.0)),
        FormulaTestCase.value(
            params={"k": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5},
            x=1.0001,
            c=0.0,
            expected=4.512985939661577e-281,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"k": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=1.0, c=0.0, expected=0.0, atol=0.0
        ),
    )
