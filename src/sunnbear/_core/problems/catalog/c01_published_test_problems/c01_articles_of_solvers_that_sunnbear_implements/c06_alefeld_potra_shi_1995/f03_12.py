"""This module holds a formula of Alefeld, Potra, Shi (1995).

The formula comes from the row with the key ``12`` in the survey of published test problems.
"""

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


class AlefeldPotraShi199512(Formula):
    """This formula comes from Alefeld, Potra, Shi (1995).

    The survey writes the source's function as ``x^(1/n) - n^(1/n)``, with the parameters ``n = 2(1)6, 7(2)33``; the
    formula's interval is ``[1, 100]``.

    Driver problem 25.
    """

    number = (1, 1, 6, 3)
    name = "12"
    params = (FormulaParam("n", latex_symbol="n"),)
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344. "
            "https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748: "
            "https://www.netlib.org/toms/748."
        ),
        location="Table I, problem 12",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 99 \c"),),
        expression=r"\tmp{u}^{\frac{1}{\param{n}}} - \param{n}^{\frac{1}{\param{n}}}",
        interval="[1, 100]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 99.0 * c
        return x ** (1 / n) - n ** (1 / n)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 100.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=(
                    (2.0,),
                    (3.0,),
                    (4.0,),
                    (5.0,),
                    (6.0,),
                    (7.0,),
                    (9.0,),
                    (11.0,),
                    (13.0,),
                    (15.0,),
                    (17.0,),
                    (19.0,),
                    (21.0,),
                    (23.0,),
                    (25.0,),
                    (27.0,),
                    (29.0,),
                    (31.0,),
                    (33.0,),
                ),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=30.7, c=0.0, expected=4.126544508504932),
        FormulaTestCase.value(params={"n": 2.0}, x=30.7, c=0.25, expected=1.0250486211569985),
        FormulaTestCase.value(params={"n": 3.0}, x=30.7, c=0.0, expected=1.6889647305566342),
        FormulaTestCase.value(params={"n": 4.0}, x=30.7, c=0.0, expected=0.9396679280333415),
        FormulaTestCase.value(params={"n": 5.0}, x=30.7, c=0.0, expected=0.603749650635323),
        FormulaTestCase.value(params={"n": 6.0}, x=30.7, c=0.0, expected=0.4215175951342829),
        FormulaTestCase.value(params={"n": 7.0}, x=30.7, c=0.0, expected=0.3105096400457152),
        FormulaTestCase.value(params={"n": 9.0}, x=30.7, c=0.0, expected=0.18645932581031444),
        FormulaTestCase.value(params={"n": 11.0}, x=30.7, c=0.0, expected=0.12161885656952544),
        FormulaTestCase.value(params={"n": 13.0}, x=30.7, c=0.0, expected=0.08323938212570105),
        FormulaTestCase.value(params={"n": 15.0}, x=30.7, c=0.0, expected=0.058582268411528776),
        FormulaTestCase.value(params={"n": 17.0}, x=30.7, c=0.0, expected=0.041795132398540685),
        FormulaTestCase.value(params={"n": 19.0}, x=30.7, c=0.0, expected=0.029862505562582648),
        FormulaTestCase.value(params={"n": 21.0}, x=30.7, c=0.0, expected=0.021094181804954037),
        FormulaTestCase.value(params={"n": 23.0}, x=30.7, c=0.0, expected=0.014479601689152816),
        FormulaTestCase.value(params={"n": 25.0}, x=30.7, c=0.0, expected=0.009382862924458743),
        FormulaTestCase.value(params={"n": 27.0}, x=30.7, c=0.0, expected=0.005386854214642424),
        FormulaTestCase.value(params={"n": 29.0}, x=30.7, c=0.0, expected=0.0022084021405079255),
        FormulaTestCase.value(params={"n": 31.0}, x=30.7, c=0.0, expected=-0.0003503871256924706),
        FormulaTestCase.value(params={"n": 33.0}, x=30.7, c=0.0, expected=-0.002431272114851467),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(1.0, 100.0)),
    )
