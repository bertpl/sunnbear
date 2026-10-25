"""This module holds a formula of Alefeld, Potra, Shi (1995).

The formula comes from the row with the key ``12`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class AlefeldPotraShi199512(Formula):
    """This formula comes from Alefeld, Potra, Shi (1995).

    The survey writes the source's function as ``x^(1/n) - n^(1/n)``, with the parameters ``n = 2(1)6, 7(2)33``; the
    formula's interval is ``[1, 100]``.

    Driver problem 25.

    Only the test problems with ``n = 27`` and ``n = 31`` have a version with ``modified = 1``, which computes the
    published function in the equivalent form ``n**(1/n) * expm1(log(x/n)/n)``, on the published interval; ``c``
    shifts x as category 1 states.

    The published test problems with ``n = 27`` and ``n = 31`` do not satisfy the benchmark suite inclusion conditions,
    because the conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a
    midpoint lands on an exact 0 of f.

    Near the root, ``x = n``, the 2 terms of the published form cancel, so that f is exactly 0 at many x-values within
    about 1e-13 of the root. Of the published values of ``n``, only for ``n = 27`` and ``n = 31`` does bisection land on
    one of these x-values. ``expm1(log(x/n)/n)`` computes ``(x/n)**(1/n) - 1`` without the subtraction.
    """

    number = (1, 1, 6, 3)
    name = "12"
    param_names = ("n", "modified")
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344. "
            "https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748: "
            "https://www.netlib.org/toms/748."
        ),
        location="12",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``n**(1/n) * expm1(log(y/n)/n)``, with ``y = x - c_scale*c``. Category 1
        states the rule for ``c_scale``.
        """
        x = x - 99.0 * c
        if modified == 1:
            return n ** (1 / n) * math.expm1(math.log(x / n) / n)
        else:
            return x ** (1 / n) - n ** (1 / n)

    def interval_bounds(self, n: float, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 100.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("n", "modified"),
                rows=(
                    (2.0, 0.0),
                    (3.0, 0.0),
                    (4.0, 0.0),
                    (5.0, 0.0),
                    (6.0, 0.0),
                    (7.0, 0.0),
                    (9.0, 0.0),
                    (11.0, 0.0),
                    (13.0, 0.0),
                    (15.0, 0.0),
                    (17.0, 0.0),
                    (19.0, 0.0),
                    (21.0, 0.0),
                    (23.0, 0.0),
                    (25.0, 0.0),
                    (27.0, 0.0),
                    (29.0, 0.0),
                    (31.0, 0.0),
                    (33.0, 0.0),
                ),
            ),
            ParamTable(names=("n", "modified"), rows=((27.0, 1.0), (31.0, 1.0))),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0, "modified": 0.0}, x=30.7, c=0.0, expected=4.126544508504932),
        FormulaTestCase.value(params={"n": 2.0, "modified": 0.0}, x=30.7, c=0.25, expected=1.0250486211569985),
        FormulaTestCase.value(params={"n": 3.0, "modified": 0.0}, x=30.7, c=0.0, expected=1.6889647305566342),
        FormulaTestCase.value(params={"n": 4.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.9396679280333415),
        FormulaTestCase.value(params={"n": 5.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.603749650635323),
        FormulaTestCase.value(params={"n": 6.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.4215175951342829),
        FormulaTestCase.value(params={"n": 7.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.3105096400457152),
        FormulaTestCase.value(params={"n": 9.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.18645932581031444),
        FormulaTestCase.value(params={"n": 11.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.12161885656952544),
        FormulaTestCase.value(params={"n": 13.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.08323938212570105),
        FormulaTestCase.value(params={"n": 15.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.058582268411528776),
        FormulaTestCase.value(params={"n": 17.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.041795132398540685),
        FormulaTestCase.value(params={"n": 19.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.029862505562582648),
        FormulaTestCase.value(params={"n": 21.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.021094181804954037),
        FormulaTestCase.value(params={"n": 23.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.014479601689152816),
        FormulaTestCase.value(params={"n": 25.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.009382862924458743),
        FormulaTestCase.value(params={"n": 27.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.005386854214642424),
        FormulaTestCase.value(params={"n": 29.0, "modified": 0.0}, x=30.7, c=0.0, expected=0.0022084021405079255),
        FormulaTestCase.value(params={"n": 31.0, "modified": 0.0}, x=30.7, c=0.0, expected=-0.0003503871256924706),
        FormulaTestCase.value(params={"n": 33.0, "modified": 0.0}, x=30.7, c=0.0, expected=-0.002431272114851467),
        FormulaTestCase.interval_bounds(params={"n": 2.0, "modified": 0.0}, expected=(1.0, 100.0)),
        FormulaTestCase.interval_bounds(params={"n": 27.0, "modified": 1.0}, expected=(1.0, 100.0)),
        FormulaTestCase.value(params={"n": 27.0, "modified": 1.0}, x=30.7, c=0.25, expected=-0.061549203181192384),
        FormulaTestCase.interval_bounds(params={"n": 31.0, "modified": 1.0}, expected=(1.0, 100.0)),
        FormulaTestCase.value(params={"n": 31.0, "modified": 1.0}, x=30.7, c=0.25, expected=-0.05792643762161267),
    )
