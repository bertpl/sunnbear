"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``aps14_f`` in the survey of published test problems. The survey describes
this function in words, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Scipy2026Aps14F(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``n/20.0*(x/1.5 + sin(x) - 1)`` (x > 0); ``-n/20.0`` (x <= 0), with the
    parameters ``n = 1, 2, ..., 40``; the formula's interval is ``[-1000, pi/2]``.

    IDs aps.14.00–aps.14.39; smoothness 0; the interval starts at -1000, where Alefeld–Potra–Shi (1995), Table I, and
    their driver start it at -10^4; for x <= 0 the code returns ``-n/20.0``, not the 0 of the docstring; derivatives
    given
    """

    number = (1, 3, 8, 7)
    name = "aps14_f"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "SciPy 1.18.1, module `scipy/optimize/_tstutils.py`, "
            "https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py. The module cites "
            "2 sources:\n"
            '- [1] Alefeld, G. E., Potra, F. A. and Shi, Y., "Algorithm 748: Enclosing Zeros of '
            'Continuous Functions", ACM Trans. Math. Softw. (1995), '
            "https://dl.acm.org/doi/10.1145/210089.210111\n"
            '- [2] Chandrupatla, T. R., "A new hybrid quadratic/bisection algorithm for finding the '
            'zero of a nonlinear function without using derivatives", Advances in Engineering Software '
            "28.3 (1997): 145-149 (no DOI in the module)"
        ),
        location="aps14_f",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1001.570796326795 * c
        if x > 0.0:
            return n / 20.0 * (x / 1.5 + math.sin(x) - 1)
        else:
            return -n / 20.0

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1000.0, 1.5707963267948966)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=(
                    (1.0,),
                    (2.0,),
                    (3.0,),
                    (4.0,),
                    (5.0,),
                    (6.0,),
                    (7.0,),
                    (8.0,),
                    (9.0,),
                    (10.0,),
                    (11.0,),
                    (12.0,),
                    (13.0,),
                    (14.0,),
                    (15.0,),
                    (16.0,),
                    (17.0,),
                    (18.0,),
                    (19.0,),
                    (20.0,),
                    (21.0,),
                    (22.0,),
                    (23.0,),
                    (24.0,),
                    (25.0,),
                    (26.0,),
                    (27.0,),
                    (28.0,),
                    (29.0,),
                    (30.0,),
                    (31.0,),
                    (32.0,),
                    (33.0,),
                    (34.0,),
                    (35.0,),
                    (36.0,),
                    (37.0,),
                    (38.0,),
                    (39.0,),
                    (40.0,),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=-699.529, c=0.0, expected=-0.05),
        FormulaTestCase.value(params={"n": 1.0}, x=-699.529, c=0.25, expected=-0.05),
        FormulaTestCase.value(params={"n": 2.0}, x=-699.529, c=0.0, expected=-0.1),
        FormulaTestCase.value(params={"n": 3.0}, x=-699.529, c=0.0, expected=-0.15),
        FormulaTestCase.value(params={"n": 4.0}, x=-699.529, c=0.0, expected=-0.2),
        FormulaTestCase.value(params={"n": 5.0}, x=-699.529, c=0.0, expected=-0.25),
        FormulaTestCase.value(params={"n": 6.0}, x=-699.529, c=0.0, expected=-0.3),
        FormulaTestCase.value(params={"n": 7.0}, x=-699.529, c=0.0, expected=-0.35),
        FormulaTestCase.value(params={"n": 8.0}, x=-699.529, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"n": 9.0}, x=-699.529, c=0.0, expected=-0.45),
        FormulaTestCase.value(params={"n": 10.0}, x=-699.529, c=0.0, expected=-0.5),
        FormulaTestCase.value(params={"n": 11.0}, x=-699.529, c=0.0, expected=-0.55),
        FormulaTestCase.value(params={"n": 12.0}, x=-699.529, c=0.0, expected=-0.6),
        FormulaTestCase.value(params={"n": 13.0}, x=-699.529, c=0.0, expected=-0.65),
        FormulaTestCase.value(params={"n": 14.0}, x=-699.529, c=0.0, expected=-0.7),
        FormulaTestCase.value(params={"n": 15.0}, x=-699.529, c=0.0, expected=-0.75),
        FormulaTestCase.value(params={"n": 16.0}, x=-699.529, c=0.0, expected=-0.8),
        FormulaTestCase.value(params={"n": 17.0}, x=-699.529, c=0.0, expected=-0.85),
        FormulaTestCase.value(params={"n": 18.0}, x=-699.529, c=0.0, expected=-0.9),
        FormulaTestCase.value(params={"n": 19.0}, x=-699.529, c=0.0, expected=-0.95),
        FormulaTestCase.value(params={"n": 20.0}, x=-699.529, c=0.0, expected=-1.0),
        FormulaTestCase.value(params={"n": 21.0}, x=-699.529, c=0.0, expected=-1.05),
        FormulaTestCase.value(params={"n": 22.0}, x=-699.529, c=0.0, expected=-1.1),
        FormulaTestCase.value(params={"n": 23.0}, x=-699.529, c=0.0, expected=-1.15),
        FormulaTestCase.value(params={"n": 24.0}, x=-699.529, c=0.0, expected=-1.2),
        FormulaTestCase.value(params={"n": 25.0}, x=-699.529, c=0.0, expected=-1.25),
        FormulaTestCase.value(params={"n": 26.0}, x=-699.529, c=0.0, expected=-1.3),
        FormulaTestCase.value(params={"n": 27.0}, x=-699.529, c=0.0, expected=-1.35),
        FormulaTestCase.value(params={"n": 28.0}, x=-699.529, c=0.0, expected=-1.4),
        FormulaTestCase.value(params={"n": 29.0}, x=-699.529, c=0.0, expected=-1.45),
        FormulaTestCase.value(params={"n": 30.0}, x=-699.529, c=0.0, expected=-1.5),
        FormulaTestCase.value(params={"n": 31.0}, x=-699.529, c=0.0, expected=-1.55),
        FormulaTestCase.value(params={"n": 32.0}, x=-699.529, c=0.0, expected=-1.6),
        FormulaTestCase.value(params={"n": 33.0}, x=-699.529, c=0.0, expected=-1.65),
        FormulaTestCase.value(params={"n": 34.0}, x=-699.529, c=0.0, expected=-1.7),
        FormulaTestCase.value(params={"n": 35.0}, x=-699.529, c=0.0, expected=-1.75),
        FormulaTestCase.value(params={"n": 36.0}, x=-699.529, c=0.0, expected=-1.8),
        FormulaTestCase.value(params={"n": 37.0}, x=-699.529, c=0.0, expected=-1.85),
        FormulaTestCase.value(params={"n": 38.0}, x=-699.529, c=0.0, expected=-1.9),
        FormulaTestCase.value(params={"n": 39.0}, x=-699.529, c=0.0, expected=-1.95),
        FormulaTestCase.value(params={"n": 40.0}, x=-699.529, c=0.0, expected=-2.0),
        FormulaTestCase.value(params={"n": 1.0}, x=1.0, c=0.0, expected=0.025406882573728157),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(-1000.0, 1.5707963267948966)),
    )
