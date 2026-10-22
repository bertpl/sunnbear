"""The formula modules' generator translates the survey's functions and reads their published cases correctly."""

import math

import mpmath
import pytest
import sympy as sp

from sunnbear._core.utils import math_functions


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
    """The Python code and the sympy expression of a function, with each construct of the translation, agree."""
    # --- arrange ----------------------
    formula_expression_cls = script_modules["formula_expressions"].FormulaExpression
    python_names = {name: f"{name}_" for name in parameters}

    # --- act --------------------------
    expression = formula_expression_cls.from_text(text, variable, python_names)
    python_values = {python_names[name]: value for name, value in parameters.items()}
    namespace = {"math": math, **vars(math_functions)}
    # the code comes from the translation of a test's own text, as the generator evaluates it
    python_value = eval(expression.python_code, namespace, {**python_values, "x": x})  # noqa: S307
    exact_expression = expression.sympy_expr.subs({sp.Symbol(name): value for name, value in parameters.items()})
    with mpmath.workdps(40):
        exact_value = float(sp.lambdify(expression.variable, exact_expression, modules="mpmath")(mpmath.mpf(x)))

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
    formula_expressions = script_modules["formula_expressions"]
    with pytest.raises(formula_expressions.TranslationError, match=expected_message):
        formula_expressions.FormulaExpression.from_text(text, "x", {})


def test_formula_expression_names_its_helper_functions(script_modules):
    """A function's Python code imports exactly the helper functions that it calls."""
    expression = script_modules["formula_expressions"].FormulaExpression.from_text("sign(x)*J0(x)^(1/3)", "x", {})
    assert expression.helper_functions == ("bessel_j0", "real_root", "sign")


def test_free_names_leaves_out_functions_constants_and_indices(script_modules):
    """The free names of a function are its variable and parameters, and `e`; never a function, `pi` or an index."""
    names = script_modules["formula_expressions"].FormulaExpression.free_names("sum(sin(i*x*pi), i = 1..3) + a*e")
    assert names == ["x", "a", "e"]


# ==================================================================================================
#  PublishedFormula
# ==================================================================================================
def test_published_formula_pairs_each_set_of_values_with_its_intervals(script_modules):
    """Sets of parameter values that name their intervals after `on` give the combinations of each set on those."""
    # --- arrange ----------------------
    row = _source_row(
        script_modules,
        "s:1",
        "x^n - a",
        parameters="on `[0, 5]`: `a = 0.2, 1`, `n = 4(2)8`; on `[-1, 4]`: `a = 1`, `n = 10`",
        interval="`[0, 5]`; `[-1, 4]`",
    )
    source, line = _source_and_line(script_modules, [row])

    # --- act --------------------------
    published = script_modules["published_cases"].PublishedFormula.from_survey(line, source)

    # --- assert -----------------------
    assert published.parameter_names == ("a", "n")
    assert [
        (tuple(float(value) for _, value in case.parameter_values), case.interval.key) for case in published.cases
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
    """A formula of several rows accepts its family form only where each row's values give that row's own `f`."""
    # --- arrange ----------------------
    published_cases = script_modules["published_cases"]
    rows = [
        _source_row(script_modules, "s:1", "if(x <= 1/3; -0.5; 0.5)", interval="[-11, 9]"),
        _source_row(script_modules, "s:2", "if(x <= 1/3; -10^-3; 1 - 10^-3)", interval="[-11, 9]"),
    ]
    function = script_modules["data_files"].FunctionDecision(f="if(x <= 1/3; -d; 1 - d)", parameters=parameters)
    source, line = _source_and_line(script_modules, rows, function)
    published = published_cases.PublishedFormula.from_survey(line, source)
    expression = script_modules["formula_expressions"].FormulaExpression.from_text(
        published.f, published.variable, {"d": "d"}
    )

    # --- act / assert -----------------
    if is_accepted:
        published.check_rows(expression, is_template=True)
    else:
        with pytest.raises(published_cases.PublicationError, match="s:1"):
            published.check_rows(expression, is_template=True)


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


def _source_and_line(script_modules, rows, function=None):
    """Return source `s` with the rows, and the line of `formulas.csv` of its formula that holds them all."""
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
    line = script_modules["formulas"].FormulasTableLine(
        number=(1, 1, 1, 1),
        source_id="s",
        row_ids=tuple(row.row_id for row in rows),
        function=function or data_files.FunctionDecision(),
        is_retired=False,
    )
    return source, line
