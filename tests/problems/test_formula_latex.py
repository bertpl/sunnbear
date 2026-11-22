"""A formula checks its parameters and its presentation at class definition, and renders the presentation's LaTeX."""

import pytest

from sunnbear._core.problems.core import (
    Formula,
    FormulaParam,
    FormulaPresentation,
    ParamAxis,
    ParamGrid,
    ParamRecipe,
)
from tests.problems.example_formulas import ExampleCubic


def _define_formula(declared_params: tuple[FormulaParam, ...], declared_presentation: FormulaPresentation | None):
    """Define and return a formula of the 2 parameters ``m`` and ``b``, with the given declarations."""

    class LineOnInterval(Formula):
        number = (99, 990)
        name = "Line on interval"
        params = declared_params
        presentation = declared_presentation
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float, m: float, b: float) -> float:
            """Return the line ``m*x - c``."""
            return m * x - c

        def interval_bounds(self, m: float, b: float) -> tuple[float, float]:
            """Return the interval ``[-b, b]``."""
            return (-b, b)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            """Return 1 grid over ``m`` and ``b``."""
            return (ParamGrid(axes=(ParamAxis("m", -1.0, 1.0, 1.0), ParamAxis("b", 1.0, 2.0, 1.0))),)

    return LineOnInterval


_PARAMS = (FormulaParam("m", latex_symbol="m"), FormulaParam("b", latex_symbol="b"))


# ==================================================================================================
#  Declarations
# ==================================================================================================
def test_param_names_come_from_params():
    """`param_names` lists the names of `params`, in order."""
    assert ExampleCubic().param_names == ("p1",)


@pytest.mark.usefixtures("isolated_formula_registry")
def test_declaring_param_names_is_rejected():
    """A formula that declares ``param_names``, which `params` derives, is rejected at class definition."""
    with pytest.raises(TypeError, match="declares param_names"):

        class LineDeclaringParamNames(Formula):
            number = (99, 991)
            name = "Line declaring param names"
            param_names = ("p1",)

            @staticmethod
            def parametrized_fun(x: float, c: float, p1: float) -> float:
                """Return ``x - c``."""
                return x - c

            def interval_bounds(self, p1: float) -> tuple[float, float]:
                """Return the interval ``[-1, 1]``."""
                return (-1.0, 1.0)

            def recipes(self) -> tuple[ParamRecipe, ...]:
                """Return 1 grid over ``p1``."""
                return (ParamGrid.decimal("p1", 0.0, 1.0, 0.5),)


@pytest.mark.usefixtures("isolated_formula_registry")
@pytest.mark.parametrize(
    "expression, interval, meaning, message",
    [
        (r"\param{m} \x - \param{w} \c", r"[-\param{b}, \param{b}]", None, r"undeclared parameters \['w'\]"),
        (r"\param{m} \x - \c", "[-1, 1]", None, r"leaves the parameters \['b'\] out"),
        (
            r"\param{m} \x - \c",
            r"[-\param{b}, \param{b}]",
            r"the slope, as $\param{s}$",
            r"undeclared parameters \['s'\]",
        ),
    ],
)
def test_presentation_must_name_exactly_the_parameters(expression, interval, meaning, message):
    """A presentation names only declared parameters, each in its definitions, expression or interval."""
    # --- arrange ----------------------
    params = (FormulaParam("m", latex_symbol="m", meaning=meaning), FormulaParam("b", latex_symbol="b"))

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        _define_formula(params, FormulaPresentation(expression=expression, interval=interval))


# ==================================================================================================
#  Rendering
# ==================================================================================================
@pytest.mark.usefixtures("isolated_formula_registry")
def test_latex_with_symbols_and_with_values():
    """The same text renders with the symbols, or with a test problem's values, substituted and not simplified."""
    # --- arrange ----------------------
    formula = _define_formula(
        _PARAMS, FormulaPresentation(expression=r"\param{m} \x - \c", interval=r"[-\param{b}, \param{b}]")
    )()
    text = r"(1 - \param{m}) \param{b}"

    # --- act --------------------------
    with_symbols = formula.latex_with_symbols(text)
    with_values = formula.latex_with_values(text, (-1.0, 2.0))

    # --- assert -----------------------
    assert with_symbols == r"(1 - \prm{m}) \prm{b}"
    assert with_values == r"(1 - \prm{(-1)}) \prm{2}"


@pytest.mark.usefixtures("isolated_formula_registry")
def test_latex_with_symbols_needs_each_symbol():
    """Rendering with symbols fails for a parameter that declares no symbol."""
    # --- arrange ----------------------
    params = (FormulaParam("m"), FormulaParam("b", latex_symbol="b"))
    formula = _define_formula(
        params, FormulaPresentation(expression=r"\param{m} \x - \c", interval=r"[-\param{b}, \param{b}]")
    )()

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"\['m'\]"):
        formula.latex_with_symbols(formula.presentation.expression)


@pytest.mark.usefixtures("isolated_formula_registry")
@pytest.mark.parametrize(
    "param_values, expected",
    [
        (None, r"\begin{aligned} \tmp{u} &= \prm{m} \x \\ f(\x, \c) &= \tmp{u} - \c \end{aligned}"),
        ((0.5, 1.0), r"\begin{aligned} \tmp{u} &= \prm{0.5} \x \\ f(\x, \c) &= \tmp{u} - \c \end{aligned}"),
    ],
)
def test_latex_display_with_definitions(param_values, expected):
    """With definitions, the display aligns 1 line per definition and the line of ``f(x, c)`` at their ``=``."""
    # --- arrange ----------------------
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\param{m} \x"),),
        expression=r"\tmp{u} - \c",
        interval=r"[-\param{b}, \param{b}]",
    )
    formula = _define_formula(_PARAMS, presentation)()

    # --- act / assert -----------------
    assert formula.latex_display(param_values) == expected


def test_latex_display_without_definitions():
    """Without definitions, the display is the 1 line ``f(x, c) = …``."""
    assert ExampleCubic().latex_display((0.4,)) == r"f(\x, \c) = \x^3 - \prm{0.4} \x - \c"


@pytest.mark.usefixtures("isolated_formula_registry")
def test_latex_display_needs_a_presentation():
    """A formula without a presentation has no display."""
    # --- arrange ----------------------
    formula = _define_formula(_PARAMS, None)()

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="declares no presentation"):
        formula.latex_display()


# ==================================================================================================
#  Texts for a reader
# ==================================================================================================
def test_texts_for_a_reader_gather_every_text():
    """A formula's texts for a reader are its meanings, its recipes' summaries and its presentation's texts."""
    assert ExampleCubic().texts_for_a_reader() == (
        r"The sweep of $\param{p1}$ from 0 to 1.",
        r"An example cubic, with 1 root for $\param{p1} \le 0$ and up to 3 roots for a larger $\param{p1}$.",
    )


@pytest.mark.usefixtures("isolated_formula_registry")
def test_texts_for_a_reader_without_a_presentation():
    """A formula without a presentation has only its meanings and its recipes' summaries as texts for a reader."""
    # --- arrange ----------------------
    params = (
        FormulaParam("m", latex_symbol="m", meaning="The slope of the line."),
        FormulaParam("b", latex_symbol="b"),
    )
    formula = _define_formula(params, None)()

    # --- act / assert -----------------
    assert formula.texts_for_a_reader() == ("The slope of the line.",)
