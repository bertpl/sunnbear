"""The formula modules' generator translates the survey's functions and reads their published test functions."""

import math

import mpmath
import pytest


# ==================================================================================================
#  FormulaExpression
# ==================================================================================================
@pytest.mark.parametrize(
    "text, variable, parameters, x",
    [
        ("sqrt(abs(x - 2/3))*if(x <= 2/3; 1; -1) - 0.1", "x", {}, 0.25),
        ("sqrt(abs(x - 2/3))*if(x <= 2/3; 1; -1) - 0.1", "x", {}, 0.75),
        ("if(x = 0; 0.0; 1/(x - 2/3))", "x", {}, 0.0),
        ("if(x = 0; 0.0; 1/(x - 2/3))", "x", {}, 0.5),
        ("(x > -0.5)*(1 + sin(1/(x + 1))) - 1", "x", {}, -0.75),
        ("(x > -0.5)*(1 + sin(1/(x + 1))) - 1", "x", {}, 0.3),
        ("1/10^3 + sum(sin(pi*i^3*x/2)/(pi*i^3), i = 1..10)", "x", {}, 0.37),
        ("10^-8*(x - 1)*prod(x^2 + x + i, i = 1..10)", "x", {}, 1.2),
        ("Phi(x - 1) - sqrt(2)/4", "x", {}, 0.4),
        ("phi(x - 1) - sqrt(2)/4", "x", {}, 0.4),
        ("x^(1/5)/(1 + abs(x)^(1/5))", "x", {}, -3.0),
        ("(x - 1)^(1/7)", "x", {}, 0.2),
        ("cbrt((4*x - 3)/x)", "x", {}, 0.5),
        ("J0(K)*Y1(K*x) - J1(K*x)*Y0(K)", "x", {"K": 2.5}, 0.6),
        ("h = exp(-h)", "h", {}, 0.4),
        ("lambda*h^2 - c", "h", {"lambda": 2.0, "c": 3.0}, 1.1),
    ],
)
def test_formula_expression_python_agrees_with_sympy(script_modules, text, variable, parameters, x):
    """For a function with each construct of the translation, the Python code and the sympy expression agree."""
    # --- arrange ----------------------
    formula_expression_cls = script_modules["formula_expressions"].FormulaExpression
    python_names = {name: f"{name}_" for name in parameters}
    python_values = {python_names[name]: value for name, value in parameters.items()}

    # --- act --------------------------
    formula_expression = formula_expression_cls.from_text(text, variable, python_names)
    python_value = formula_expression.python_value(x, python_values)
    with mpmath.workdps(40):
        exact_value = float(formula_expression.mpmath_function(parameters)(mpmath.mpf(x)))

    # --- assert -----------------------
    assert math.isclose(python_value, exact_value, rel_tol=1e-13, abs_tol=1e-13)


@pytest.mark.parametrize(
    "text, expected_message",
    [
        ("sum(x^n, n = -inf..inf)", "has no range of integers"),
        ("foo(x) - 1", "the function foo has no Python form"),
        ("x - y", "the name y is neither the variable, a parameter nor a constant"),
        ("if(x <= 0; 1)", "does not hold 3 parts"),
        ("x = 1 = 2", "has several equals signs"),
        ("(x - 1", "leaves a bracket open"),
    ],
)
def test_formula_expression_rejects_what_it_cannot_translate(script_modules, text, expected_message):
    """`FormulaExpression.from_text` raises `TranslationError` for a text that it cannot translate."""
    # --- arrange ----------------------
    formula_expressions = script_modules["formula_expressions"]

    # --- act / assert -----------------
    with pytest.raises(formula_expressions.TranslationError, match=expected_message):
        formula_expressions.FormulaExpression.from_text(text, "x", {})


def test_formula_expression_names_its_sunnbear_math_functions(script_modules):
    """A function's Python code imports exactly the functions of `math_functions` that it calls."""
    formula_expression = script_modules["formula_expressions"].FormulaExpression.from_text(
        "sign(x)*J0(x)^(1/3)", "x", {}
    )
    assert formula_expression.sunnbear_math_functions == ("bessel_j0", "real_root", "sign")


def test_free_names_leaves_out_functions_constants_and_indices(script_modules):
    """The free names of a function are its variable and parameters, and `e`; never a function, `pi` or an index."""
    names = script_modules["formula_expressions"].FormulaExpression.free_names("sum(sin(i*x*pi), i = 1..3) + a*e")
    assert names == ["x", "a", "e"]


# ==================================================================================================
#  PublishedFormula
# ==================================================================================================
def test_published_formula_pairs_each_set_of_values_with_its_intervals(script_modules):
    """Each set of parameter values that names its intervals after `on` gives its combinations on those intervals."""
    # --- arrange ----------------------
    row = _source_row(
        script_modules,
        "s:1",
        "x^n - a",
        parameters="on `[0, 5]`: `a = 0.2, 1`, `n = 4(2)8`; on `[-1, 4]`: `a = 1`, `n = 10`",
        interval="`[0, 5]`; `[-1, 4]`",
    )
    survey_formula = _survey_formula(script_modules, [row])

    # --- act --------------------------
    published = script_modules["published_test_functions"].PublishedFormula.from_survey(survey_formula)

    # --- assert -----------------------
    assert published.survey_parameter_names == ("a", "n")
    assert [
        (tuple(float(value) for _, value in test_function.parameter_values), test_function.interval.key)
        for test_function in published.test_functions
    ] == [
        ((0.2, 4.0), ("0", "5")),
        ((0.2, 6.0), ("0", "5")),
        ((0.2, 8.0), ("0", "5")),
        ((1.0, 4.0), ("0", "5")),
        ((1.0, 6.0), ("0", "5")),
        ((1.0, 8.0), ("0", "5")),
        ((1.0, 10.0), ("-1", "4")),
    ]


@pytest.mark.parametrize(
    "parameters, is_accepted",
    [
        ("d = 0.5 | d = 10^-3", True),
        ("d = 0.4 | d = 10^-3", False),
    ],
)
def test_published_formula_checks_that_each_row_gives_its_function(script_modules, parameters, is_accepted):
    """A formula of several rows accepts its line's `f` only where it equals each row's own `f` at that row's values."""
    # --- arrange ----------------------
    published_test_functions = script_modules["published_test_functions"]
    rows = [
        _source_row(script_modules, "s:1", "if(x <= 1/3; -0.5; 0.5)", interval="[-11, 9]"),
        _source_row(script_modules, "s:2", "if(x <= 1/3; -10^-3; 1 - 10^-3)", interval="[-11, 9]"),
    ]
    function_decision = script_modules["data_files"].FunctionDecision(
        f="if(x <= 1/3; -d; 1 - d)", parameters=parameters
    )
    survey_formula = _survey_formula(script_modules, rows, function_decision)

    # --- act / assert -----------------
    if is_accepted:
        published_test_functions.PublishedFormula.from_survey(survey_formula)
    else:
        with pytest.raises(published_test_functions.PublishedTestFunctionsError, match="s:1"):
            published_test_functions.PublishedFormula.from_survey(survey_formula)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _source_row(script_modules, row_id, f, *, parameters="", interval="[0, 1]"):
    """Return a row of source `s` with the given function, parameters and interval."""
    return script_modules["data_files"].SourceRow(
        row_id=row_id,
        key=row_id.split(":")[1],
        f=f,
        f_description="",
        name="",
        parameters=parameters,
        interval=interval,
        also_in="",
        notes="",
    )


def _survey_formula(script_modules, rows, function_decision=None):
    """Return the `SurveyFormula` of source `s`, whose 1 formula holds all the rows."""
    data_files = script_modules["data_files"]
    source = data_files.Source(
        source_id="s",
        title="S (2000): s",
        reference="S (2000).",
        year=2000,
        subcategory="1.1",
        where_in_source="",
        transcribed_from="",
        rows_summary="",
        notes="",
        relations=(),
        rows=tuple(rows),
    )
    formulas_module = script_modules["formulas"]
    line = formulas_module.FormulasTableLine(
        number=(1, 1, 1, 1),
        source_id="s",
        row_ids=tuple(row.row_id for row in rows),
        function_decision=function_decision or data_files.FunctionDecision(),
        is_retired=False,
    )
    return formulas_module.SurveyFormula(line, source)
