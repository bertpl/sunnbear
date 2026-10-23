"""This module writes the modules of category 1's formulas into sunnbear's formula catalog, from the survey.

Run it from the repo root, naming the sources whose formulas to write:

    uv run python -m scripts.literature_test_problems.formula_modules 1971_dowell_jarratt_illinois

For each named source, the script:

- writes the source's category package below `CATALOG_DIR`, with 1 module per active formula of the source in
  `formulas.csv`;
- rewrites the `__init__.py` of each subcategory, so that it imports every source package present;
- formats every file that it wrote with ruff.

The README of `data/literature_test_problems/` (§ Formula modules) describes what a generated formula module holds,
which formulas are written by hand, and which formulas the script cannot generate.
"""

import ast
import hashlib
import json
import keyword
import math
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import mpmath
import sympy as sp

from sunnbear._core.functions.core.test_cases import DEFAULT_ATOL
from sunnbear._core.utils import math_functions
from sunnbear._core.utils.slugify import slugify
from sunnbear.functions import CANONICAL_DIGITS, ParamNotation

from .data_files import SUBCATEGORY_DESCRIPTIONS, DataFolder, Source, SourceRow, read_sources
from .formula_expressions import FormulaExpression, TranslationError
from .formulas import FormulasTable, FormulasTableLine, SurveyFormula
from .intervals import ParsedIntervals
from .published_test_functions import PublishedFormula, PublishedTestFunction, PublishedTestFunctionsError

CATALOG_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "sunnbear" / "_core" / "functions" / "catalog"
) / "c01_published_test_functions"
# UNTRANSLATABLE_FORMULAS holds, with the reason, each formula whose rows give an `f`, `parameters` or `variable_change`
# that the script cannot translate, and whose module is therefore written by hand.
UNTRANSLATABLE_FORMULAS = {
    "f1.1.2.4": "an infinite sum, which the module sums until its terms vanish in float64",
    "f1.1.11.2": "a function `alpha` that the row's parameters define",
    "f1.2.18.14": "a product written with `...`",
    "f1.2.19.3": "the stated root `x*` as a parameter",
    "f1.2.19.6": "noise of a stated distribution, which the module takes from `normal_noise`",
    "f1.2.20.2": "a normal cumulative distribution function with a mean and a variance, `Phi(x; mu, sigma^2)`",
    "f1.2.20.3": "parameters given as sets, `{a0, a1, a2, a3, m} = {...}`",
    "f1.4.1.7": (
        "a removable singularity at its root `x = 1`, where the expression divides by 0 and the formula needs the "
        "limit 0"
    ),
    "f1.4.4.7": (
        "constants named in words (the initial investment, the monthly deposit and the goal), with several sets of "
        "values"
    ),
    "f1.4.6.6": "a change of its variable to the pH, as `f(10^-pH)`",
    "f1.4.6.7": "a parameter given as a ratio, `q/q0 = 0.01`",
    "f1.4.6.8": "a parameter defined by a formula of the other parameters, `Re = rho*V*D/mu`",
    "f1.4.6.9": "a variable named `f`, and a parameter defined by a formula of the other parameters, `Re = rho*V*D/mu`",
    "f1.4.6.22": (
        "variables that depend on the unknown `y`, `B = 3 + y` and `Ac = 3*y + y^2/2`, which the row lists among its "
        "parameters"
    ),
    "f1.4.6.24": "a change of its variable to the temperature `T` in °C, as `f(T + 273.15)`",
    "f1.4.7.1": "a variable named `lambda`, a keyword of Python",
}
# CASE_FRACTIONS are the positions in the interval, as fractions of its width, at which the cases are tried, in
# order; of the positions whose cases meet the strictest tolerance, `FormulaModuleSpec._find_case` keeps the first where
# the case discriminates, or else the first. Every fraction is at least `SHIFTED_CASE_C`, so that the shifted x-value of
# a case stays in the interval.
CASE_FRACTIONS = (0.3, 0.7, 0.45, 0.85, 0.6, 0.35)
# SHIFTED_CASE_C is the value of c of the 1 case per formula that exercises the shift of x.
SHIFTED_CASE_C = 0.25
# BRANCH_CASE_GAP is how far, relative to its size, a branch case's x-value lies beside a value that a condition
# compares x with, so that float64 and mpmath take the same branch there.
BRANCH_CASE_GAP = 1e-9
# CASE_RTOL and CASE_ATOL bound how far the generated Python may be from mpmath at a case's x-value: 10 times smaller
# than the default tolerances of the generic formula test, so that the numba-compiled function, whose result may
# differ slightly from the Python one, still passes that test.
CASE_RTOL = 1e-13
CASE_ATOL = 1e-13
# CASE_X_ULPS is the number of float64 steps of x, on each side of a case's x-value, over which
# `FormulaModuleSpec._case_tolerance` measures the spread of the function's exact values.
CASE_X_ULPS = 4
# CASE_ROUNDING_UNITS is the number of units of float64 rounding by which `FormulaModuleSpec._case_tolerance` lets a
# case's Python value differ from its exact value where the function cancels, as an expanded polynomial does near a
# multiple root. A unit is 2^-53 times the magnitude of the function's terms
# (`FormulaExpression.mpmath_term_magnitude_function`).
CASE_ROUNDING_UNITS = 16
# CASE_SMALL_VALUE is the size below which a case's expected value tests little: the generic formula test's default
# `atol` accepts any value within `DEFAULT_ATOL` of the expected value, 0 among them.
CASE_SMALL_VALUE = 1000 * DEFAULT_ATOL
# CASE_X_STEP_FRACTION and CASE_MIN_RELATIVE_CHANGE decide whether a case discriminates, by testing how the function
# depends on x: the function's value must change by more than `CASE_MIN_RELATIVE_CHANGE` of itself when x moves by
# `CASE_X_STEP_FRACTION` of the interval's width. Where it does not, such as at x = 0.2 for `35*x^35 - 1`, the terms in
# x are below the test's tolerance.
CASE_X_STEP_FRACTION = 0.01
CASE_MIN_RELATIVE_CHANGE = 1e-9
# DOCSTRING_WIDTH is the width of a wrapped docstring line, inside a class at 4 spaces of indentation.
DOCSTRING_WIDTH = 120 - 4
# C_SCALE_DIGITS is the number of significant digits of `c_scale`, the scale of a formula's shift along x: the width of
# the formula's interval, rounded. The class docstring of `PublishedTestFunctions`, category 1, states the rule.
C_SCALE_DIGITS = 3
# RESERVED_NAMES are the names that a parameter of the source may not keep, because the formula module uses them.
RESERVED_NAMES = {"x", "c", "c_scale", "self", "math", *math_functions.__all__}
# INTERVAL_BOUND_NAMES are the names of the bounds of a formula's interval: the class docstring of category 1 names a
# formula's interval `[a, b]`, and a formula with several intervals takes its bounds as the parameters `a` and `b`, so
# that a parameter of the source may not keep these names either.
INTERVAL_BOUND_NAMES = {"a", "b"}
# GENERATED_PACKAGE_NOTE ends the module docstring of each generated package's `__init__.py`.
GENERATED_PACKAGE_NOTE = (
    "A script generates this {kind} from the survey of published test problems: to change it, change the survey and "
    "run `scripts/literature_test_problems/formula_modules.py`; do not edit this file."
)


class GenerationError(Exception):
    """A `GenerationError` reports a formula that the script cannot generate."""


# ==================================================================================================
#  FormulaModuleSpec
# ==================================================================================================
@dataclass(frozen=True)
class FormulaModuleSpec:
    """A `FormulaModuleSpec` holds the contents of 1 generated formula module.

    Attributes:
        formula_expression: The formula's function as Python code and as a sympy expression.
        param_names: The Python names of the formula's parameters, in tuple order; a formula with several
            intervals ends them with `a`, `b` and `c_scale`.
        renamed_parameters: Each parameter whose Python name differs from its survey name, as the pair of its survey
            name and its Python name.
        interval: The single interval of a formula that has 1, and None otherwise.
        exact_texts_of_rounded_values: The exact text of each parameter value or bound that the tuples round to
            `CANONICAL_DIGITS` significant digits.
        cases: Each case as the Python code of a `FormulaTestCase` factory call.
    """

    survey_formula: SurveyFormula
    formula_expression: FormulaExpression
    param_names: tuple[str, ...]
    renamed_parameters: tuple[tuple[str, str], ...]
    tuples: tuple[tuple[float, ...], ...]
    interval: tuple[float, float] | None
    exact_texts_of_rounded_values: tuple[str, ...]
    cases: tuple[str, ...]

    def module_text(self, formula_name: str) -> str:
        """Return the formula's module as Python source, before ruff formats it.

        `formula_name`, from `formula_names`, names the formula and its class.
        """
        source, rows = self.survey_formula.source, self.survey_formula.rows
        location = ", ".join(row.key for row in rows)
        command = f"uv run python -m scripts.literature_test_problems.formula_modules {source.source_id}"
        # a key is the source's own label or a label that the survey made from the source's sections and positions,
        # and no survey field tells which, so the docstring names the key as the survey's
        keys_text = _join_words([f"``{row.key}``" for row in rows])
        if len(rows) == 1:
            rows_text = f"the row with the key {keys_text}"
        else:
            rows_text = f"the rows with the keys {keys_text}"
        module_docstring = (
            f"This module holds a formula of {source.short_title}.\n\n"
            f"The formula comes from {rows_text} in the survey of published test problems. A script generates this "
            "module from that survey: to change the formula, change its source file in "
            f"`data/literature_test_problems/sources/` and run `{command}`; do not edit this file."
        )
        needs_math_import = "math." in self.formula_expression.python_code
        has_positive_atol_case = any("atol=" in case and "atol=0.0)" not in case for case in self.cases)
        has_zero_atol_case = any("atol=0.0)" in case for case in self.cases)
        sunnbear_math_functions = self.formula_expression.sunnbear_math_functions
        imported_names = ["Formula", "FormulaSource", "FormulaTestCase", "ParamRecipe"]
        if self.param_names:
            imported_names.append("ParamTable")
        if self.interval is None:
            c_scale_code = "c_scale"
        else:
            c_scale_code = repr(self._c_scale(self.interval))
        class_name = source_category_class_name(source) + _camel_case(slugify(formula_name))
        signature = "".join(f", {param_name}: float" for param_name in self.param_names)
        return "\n".join(
            [
                _docstring(module_docstring, width=120),
                "",
                *(["import math", ""] if needs_math_import else []),
                f"from sunnbear._core.functions.core import {', '.join(imported_names)}",
                *(
                    [f"from sunnbear._core.utils.math_functions import {', '.join(sunnbear_math_functions)}"]
                    if sunnbear_math_functions
                    else []
                ),
                "",
                "# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the",
                "# survey, so that a test fails when the survey changes and this module is not regenerated.",
                f'SURVEY_FIELDS_HASH = "{self.survey_fields_hash(self.survey_formula)}"',
                "",
                "",
                f"class {class_name}(Formula):",
                textwrap.indent(_docstring(self._class_docstring(), width=DOCSTRING_WIDTH), "    "),
                "",
                f"    number = {self.survey_formula.formulas_table_line.number!r}",
                f"    name = {formula_name!r}",
                f"    param_names = {self.param_names!r}",
                "    source = FormulaSource(",
                f"        reference={_string_code(source.reference, width=90)},",
                f"        location={_string_code(location, width=90)},",
                "    )",
                "",
                "    @staticmethod",
                f"    def parametrized_fun(x: float, c: float{signature}) -> float:",
                '        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for '
                '``c_scale``."""',
                *self._parametrized_fun_body(c_scale_code),
                "",
                f"    def interval_bounds(self{signature}) -> tuple[float, float]:",
                *self._interval_bounds_body(),
                "",
                "    def recipes(self) -> tuple[ParamRecipe, ...]:",
                *self._recipes_body(),
                "",
                *(
                    [
                        "    # a case with a positive `atol` lies where float64 cannot evaluate the function to the",
                        "    # default tolerance, because the function is ill-conditioned there or its terms cancel",
                    ]
                    if has_positive_atol_case
                    else []
                ),
                *(
                    [
                        "    # a case with `atol=0.0` has an expected value so small that the default `atol`",
                        "    # would accept any value near 0, 0 among them",
                    ]
                    if has_zero_atol_case
                    else []
                ),
                "    cases = (",
                *(f"        {case}," for case in self.cases),
                "    )",
                "",
            ]
        )

    @staticmethod
    def survey_fields_hash(survey_formula: SurveyFormula) -> str:
        """Return a hash of the formula's survey fields: every field of the survey that its generated module depends on.

        The tests recompute the hash and compare it with the module's `SURVEY_FIELDS_HASH`, so that a module left stale
        after a change of the survey fails them. A row's id holds its key, so the hash covers the key too.

        Raises:
            DataFileError: If the source lacks 1 of the formula's rows.
        """
        source = survey_formula.source
        function_decision = survey_formula.formulas_table_line.function_decision
        fields = [
            source.title,
            source.reference,
            [function_decision.variable_change, function_decision.f, function_decision.parameters],
            [
                [row.row_id, row.f, row.f_description, row.parameters, row.interval, row.notes]
                for row in survey_formula.rows
            ],
        ]
        return hashlib.sha256(json.dumps(fields).encode("utf-8")).hexdigest()[:16]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _class_docstring(self) -> str:
        """Return the class docstring: the formula's source, the rows' functions and values, and their notes."""
        rows = self.survey_formula.rows
        paragraphs = [f"This formula comes from {self.survey_formula.source.short_title}."]
        # the survey's interval may be the span between a source's 2 starting values, so the docstring does not claim
        # that the source prints the interval
        if len(rows) == 1:
            paragraphs.append(f"The survey writes the source's function as {self._row_text(rows[0])}.")
        else:
            formulas_table_line = self.survey_formula.formulas_table_line
            function_decision = formulas_table_line.function_decision
            if function_decision.f:
                # the family form and its parameter names come from `formula_decisions.csv`, not from the source
                paragraphs.append(
                    f"The source prints {len(rows)} functions that differ only in the values of some constants; with "
                    f"those constants replaced by parameters, the {len(rows)} functions become 1 function, "
                    f"``{function_decision.f}``:"
                )
            else:
                paragraphs.append(f"The source prints 1 function in {len(rows)} rows, each on its own interval:")
            values_per_row = formulas_table_line.values_per_row()
            paragraphs.append(
                "\n".join(
                    f"- {row.key}" + (f", with ``{values}``" if values else "") + f": {self._row_text(row)}"
                    for row, values in zip(rows, values_per_row, strict=True)
                )
            )
        if self.renamed_parameters:
            paragraphs.append(self._renamed_parameters_text())
        if self.exact_texts_of_rounded_values:
            paragraphs.append(self._rounded_values_text())
        for row in rows:
            if row.notes.strip() and len(rows) == 1:
                paragraphs.append(row.notes.strip())
            elif row.notes.strip():
                paragraphs.append(f"{row.key}: {row.notes.strip()}")
        return "\n\n".join(paragraphs)

    def _renamed_parameters_text(self) -> str:
        """Return 1 sentence per reason for a rename, which names the renamed parameters of the source."""
        renames_by_reason: dict[str, list[tuple[str, str]]] = {}
        for survey_name, python_name in self.renamed_parameters:
            if keyword.iskeyword(survey_name):
                reason = f"``{survey_name}`` is a Python keyword"
            elif survey_name in INTERVAL_BOUND_NAMES:
                reason = "``[a, b]`` names the formula's interval"
            else:
                reason = f"the formula uses ``{survey_name}`` for another value"
            renames_by_reason.setdefault(reason, []).append((survey_name, python_name))
        sentences = []
        for reason, renames in renames_by_reason.items():
            survey_names = _join_words([f"``{survey_name}``" for survey_name, _ in renames])
            python_names = _join_words([f"``{python_name}``" for _, python_name in renames])
            if len(renames) == 1:
                subject = f"The formula's parameter {python_names} is"
            else:
                subject = f"The formula's parameters {python_names} are"
            sentences.append(f"{subject} the source's {survey_names}, renamed because {reason}.")
        return " ".join(sentences)

    def _rounded_values_text(self) -> str:
        """Return the sentence that names the tuples' rounded values and the significant digits that they keep."""
        rounded_values = ", ".join(f"``{value}``" for value in self.exact_texts_of_rounded_values)
        if len(self.exact_texts_of_rounded_values) == 1:
            subject = f"The value {rounded_values} is"
        else:
            subject = f"The values {rounded_values} are"
        return f"{subject} rounded to {CANONICAL_DIGITS} significant digits, the most that a parameter value holds."

    @staticmethod
    def _row_text(row: SourceRow) -> str:
        """Return a row's function, its parameters and its intervals, as the docstring states them.

        The interval text and the parameters text are wrapped in double backticks unless they hold backticks already.
        """
        interval_text, parameters_text = row.interval.strip(), row.parameters.strip()
        if "`" not in interval_text:
            interval_text = f"``{interval_text}``"
        if len(ParsedIntervals.from_source_row(row).intervals) > 1:
            intervals_clause = f"the formula's intervals are {interval_text}"
        else:
            intervals_clause = f"the formula's interval is {interval_text}"
        if not parameters_text:
            return f"``{row.f}``; {intervals_clause}"
        elif parameters_text.startswith("on "):
            return f"``{row.f}``, with the parameters given per interval, {parameters_text}; {intervals_clause}"
        elif "`" in parameters_text:
            return f"``{row.f}``, with the parameters {parameters_text}; {intervals_clause}"
        else:
            return f"``{row.f}``, with the parameters ``{parameters_text}``; {intervals_clause}"

    def _parametrized_fun_body(self, c_scale_code: str) -> list[str]:
        """Return the lines of `parametrized_fun` after its docstring: the shift of x, then the function's value.

        The lines differ for 2 forms of the function:

        - when the published function is `x` itself, the method returns the shifted x directly, because assigning x
          only to return it breaks ruff's rule RET504;
        - when the whole Python expression is a conditional `a if condition else b`, the method writes it as an `if`
          statement with a `return` in each branch, so that each branch stands on its own line. A conditional
          inside a larger expression stays a conditional expression, because an `if` statement cannot stand inside an
          expression.
        """
        expression_node = ast.parse(self.formula_expression.python_code, mode="eval").body
        if self.formula_expression.python_code.strip() == "x":
            return [f"        return x - {c_scale_code} * c"]
        elif isinstance(expression_node, ast.IfExp):
            return [
                f"        x = x - {c_scale_code} * c",
                f"        if {ast.unparse(expression_node.test)}:",
                f"            return {ast.unparse(expression_node.body)}",
                "        else:",
                f"            return {ast.unparse(expression_node.orelse)}",
            ]
        else:
            return [
                f"        x = x - {c_scale_code} * c",
                f"        return {self.formula_expression.python_code}",
            ]

    def _interval_bounds_body(self) -> list[str]:
        """Return the lines of `interval_bounds`: the formula's single interval, or the tuple's own `a` and `b`."""
        if self.interval is not None:
            return [
                '        """Return the formula\'s interval."""',
                f"        return ({self.interval[0]!r}, {self.interval[1]!r})",
            ]
        else:
            return [
                '        """Return the interval of the tuple, its parameters ``a`` and ``b``."""',
                "        return (a, b)",
            ]

    def _recipes_body(self) -> list[str]:
        """Return the lines of `recipes`: 1 `ParamTable` of the published tuples, or none without parameters."""
        if self.param_names:
            tuples_code = ", ".join(repr(param_tuple) for param_tuple in self.tuples)
            if len(self.tuples) == 1:
                tuples_code += ","
            return [
                '        """Return the published parameter values."""',
                f"        return (ParamTable(names={self.param_names!r}, rows=({tuples_code})),)",
            ]
        else:
            return [
                '        """Return no recipe, since the published function has no parameters."""',
                "        return ()",
            ]

    @staticmethod
    def _python_parameter_names(survey_names: tuple[str, ...]) -> dict[str, str]:
        """Return the Python name of each survey parameter: its own name, with `_` added while that name is taken.

        A name is taken when it is a Python keyword, 1 of `RESERVED_NAMES`, or 1 of `INTERVAL_BOUND_NAMES`.
        """
        reserved = RESERVED_NAMES | INTERVAL_BOUND_NAMES
        python_names = {}
        for name in survey_names:
            python_name = name
            while python_name in reserved or keyword.iskeyword(python_name):
                python_name += "_"
            python_names[name] = python_name
        return python_names

    @staticmethod
    def _c_scale(interval: tuple[float, float]) -> float:
        """Return the formula's `c_scale` for an interval: its width, rounded to `C_SCALE_DIGITS` significant digits."""
        a, b = interval
        return float(f"{b - a:.{C_SCALE_DIGITS}g}")

    @staticmethod
    def _parameter_value(value: sp.Expr) -> tuple[float, bool]:
        """Return a published value as a float that a parameter holds, and whether that float is rounded.

        A value that no `ParamNotation` holds exactly, such as `pi`, is rounded to `CANONICAL_DIGITS` significant
        digits, as `ParamNotation.DECIMAL` rounds it.
        """
        number = float(sp.N(value, 30))
        if ParamNotation.is_valid_value(number):
            return number, False
        else:
            return ParamNotation.DECIMAL.build_value_from_argument(number), True

    @staticmethod
    def _exact_text(value: sp.Expr) -> str:
        """Return a published value's text as the survey writes it: Euler's number as e, where sympy prints E."""
        return str(sp.sympify(value).subs(sp.E, sp.Symbol("e")))

    @classmethod
    def _find_case(
        cls,
        exact_function: object,
        term_magnitude_function: object,
        formula_expression: FormulaExpression,
        python_values: dict[str, float],
        interval: tuple[float, float],
        c: float,
    ) -> tuple[float, float, float | None]:
        """Return an x-value in the interval, the formula's value there, and the `atol` that the case needs, if any.

        The x-values tried are `CASE_FRACTIONS` of the interval, rounded to 6 significant digits. The generated Python
        code and mpmath both evaluate the function at the float `x - c_scale*c`, computed as the generated code computes
        it, so that only the function's own arithmetic can differ.

        The case takes the x-value whose exact and Python values meet the strictest tolerance (`_case_tolerance`);
        among the x-values that meet the same tolerance, it takes the first one where the case discriminates
        (`_is_discriminating_case`), and otherwise the first one.

        `term_magnitude_function` is the function of the variable that
        `FormulaExpression.mpmath_term_magnitude_function` returns, from which `_case_tolerance` bounds the float64
        rounding of the function.

        Raises:
            GenerationError: If the function is complex at an x-value tried, or the generated Python code agrees with
                mpmath at none.
        """
        a, b = interval
        candidates = []
        for fraction in CASE_FRACTIONS:
            x = float(f"{a + fraction * (b - a):.6g}")
            shifted = x - cls._c_scale(interval) * c
            if a < x < b:
                values = cls._case_values(exact_function, formula_expression, python_values, shifted)
            else:
                values = None
            if values is not None:
                tolerance = cls._case_tolerance(exact_function, term_magnitude_function, shifted, *values)
                if tolerance is not None:
                    rank, atol = tolerance
                    is_discriminating = cls._is_discriminating_case(exact_function, shifted, values[0], b - a)
                    candidates.append((rank, not is_discriminating, x, values[0], atol))
        if candidates:
            _, _, x, expected, atol = min(candidates, key=lambda candidate: candidate[:2])
            return x, expected, atol
        else:
            raise GenerationError(f"the Python form agrees with mpmath at none of the x-values tried, c = {c}")

    @staticmethod
    def _case_values(
        exact_function: object, formula_expression: FormulaExpression, python_values: dict[str, float], x: float
    ) -> tuple[float, float] | None:
        """Return the exact value at x, rounded to float64, and the Python value, or None if either fails.

        Raises:
            GenerationError: If the function is complex at x.
        """
        try:
            with mpmath.workdps(50):
                exact_value = mpmath.mpmathify(exact_function(mpmath.mpf(x)))
            python_value = formula_expression.python_value(x, python_values)
        except (ArithmeticError, ValueError, TypeError):
            return None
        if isinstance(exact_value, mpmath.mpc) and abs(exact_value.imag) > 1e-30 * abs(exact_value):
            raise GenerationError(f"the function is complex at x = {x!r}")
        expected = float(mpmath.re(exact_value))
        if math.isfinite(expected) and isinstance(python_value, float):
            return expected, python_value
        else:
            return None

    @staticmethod
    def _case_tolerance(
        exact_function: object, term_magnitude_function: object, x: float, expected: float, python_value: float
    ) -> tuple[int, float | None] | None:
        """Return the strictest tolerance that a case at x meets, as its rank and its `atol`, or None if it meets none.

        The tolerances are, from the strictest:

        - rank 0: `CASE_RTOL` and `CASE_ATOL`, with no `atol` of the case's own, for an expected value of at least
          `CASE_SMALL_VALUE`; `CASE_RTOL` alone, with an `atol` of 0, for a smaller expected value, so that the test
          compares the values relatively;
        - rank 1: the function's spread over `CASE_X_ULPS` float64 steps of x, with an `atol` of 10 times that spread,
          since float64 arithmetic cannot do better there;
        - rank 2: `CASE_ROUNDING_UNITS` times 2^-53 times the summed magnitude of the function's terms
          (`term_magnitude_function`), with an `atol` of twice that bound: the function's terms cancel there, and
          float64 cannot evaluate it better;
        - rank 3: `CASE_RTOL` and `CASE_ATOL`, with no `atol` of the case's own, for an expected value below
          `CASE_SMALL_VALUE`: the generic formula test's default `atol` then accepts any value near 0, so the case tests
          little.
        """
        is_small = abs(expected) < CASE_SMALL_VALUE
        if is_small and math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=0.0):
            return 0, 0.0
        elif not is_small and math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=CASE_ATOL):
            return 0, None
        else:
            difference = abs(python_value - expected)
            spread = FormulaModuleSpec._value_spread(exact_function, x, expected)
            with mpmath.workdps(50):
                term_magnitude = float(mpmath.re(term_magnitude_function(mpmath.mpf(x))))
            rounding_bound = CASE_ROUNDING_UNITS * 2.0**-53 * term_magnitude
            if difference <= spread:
                return 1, float(f"{10 * spread:.1g}")
            elif difference <= rounding_bound:
                return 2, float(f"{2 * rounding_bound:.1g}")
            elif math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=CASE_ATOL):
                return 3, None
            else:
                return None

    @staticmethod
    def _value_spread(exact_function: object, x: float, expected: float) -> float:
        """Return how far the function's exact value moves from `expected` within `CASE_X_ULPS` float64 steps of x."""
        spread = 0.0
        with mpmath.workdps(50):
            for k in range(-CASE_X_ULPS, CASE_X_ULPS + 1):
                try:
                    value = mpmath.re(exact_function(mpmath.mpf(x) + k * mpmath.mpf(math.ulp(x))))
                except (ArithmeticError, ValueError, TypeError):
                    continue
                spread = max(spread, abs(float(value) - expected))
        return spread

    @staticmethod
    def _is_discriminating_case(exact_function: object, x: float, expected: float, interval_width: float) -> bool:
        """Return whether a case at x discriminates: whether an implementation with wrong terms in x would fail it.

        The case does not discriminate where either of these holds:

        - its expected value is below `CASE_SMALL_VALUE`;
        - the function's value changes by less than `CASE_MIN_RELATIVE_CHANGE` of itself when x moves by
          `CASE_X_STEP_FRACTION` of `interval_width`, in the first direction, up then down, where the function is
          defined.

        Where the function is defined in neither direction, the case counts as discriminating.
        """
        if abs(expected) < CASE_SMALL_VALUE:
            return False
        else:
            with mpmath.workdps(50):
                for step in (CASE_X_STEP_FRACTION * interval_width, -CASE_X_STEP_FRACTION * interval_width):
                    try:
                        moved_value = float(mpmath.re(exact_function(mpmath.mpf(x) + step)))
                    except (ArithmeticError, ValueError, TypeError):
                        continue
                    if math.isfinite(moved_value):
                        return abs(moved_value - expected) > CASE_MIN_RELATIVE_CHANGE * abs(expected)
            return True

    @staticmethod
    def _find_branch_case(
        exact_function: object,
        formula_expression: FormulaExpression,
        python_values: dict[str, float],
        interval: tuple[float, float],
        condition: ast.expr,
        is_condition_met: bool,
    ) -> tuple[float, float] | None:
        """Return an x-value in the interval where `condition` is `is_condition_met`, and the formula's value there.

        The case is for c = 0, and makes a test case reach a branch of a function that is 1 conditional. The x-values
        tried are the interval's bounds, each value that the condition compares x with, the values `BRANCH_CASE_GAP`
        beside each of those, and `CASE_FRACTIONS` of the interval; the first where the generated Python code agrees
        with mpmath within `CASE_RTOL` and `CASE_ATOL` is kept. The result is None if none is found.
        """
        a, b = interval
        namespace = {"math": math, **vars(math_functions), **python_values}
        compared_values = []
        for node in ast.walk(condition):
            if isinstance(node, ast.Compare):
                for side in (node.left, *node.comparators):
                    if not any(isinstance(name, ast.Name) and name.id == "x" for name in ast.walk(side)):
                        compared_values.append(float(eval(ast.unparse(side), namespace)))
        candidates = [a, b]
        for value in compared_values:
            gap = BRANCH_CASE_GAP * max(1.0, abs(value))
            candidates += [value, value - gap, value + gap]
        candidates += [float(f"{a + fraction * (b - a):.6g}") for fraction in CASE_FRACTIONS]
        for x in candidates:
            if not a <= x <= b or eval(ast.unparse(condition), namespace, {"x": x}) != is_condition_met:
                continue
            try:
                with mpmath.workdps(50):
                    expected = float(mpmath.re(exact_function(mpmath.mpf(x))))
                python_value = formula_expression.python_value(x, python_values)
            except (ArithmeticError, ValueError, TypeError):
                continue
            if math.isfinite(expected) and math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=CASE_ATOL):
                return x, expected
        return None

    @classmethod
    def _tuple_values(
        cls, published_test_function: PublishedTestFunction, has_interval_parameters: bool
    ) -> tuple[tuple[float, ...], tuple[float, float], list[str], dict[str, sp.Expr]]:
        """Return a published test function's parameter tuple and bounds, and the values that the module's text needs.

        A parameter value that no `ParamNotation` holds exactly is rounded by `_parameter_value`, and mpmath evaluates
        the function at the rounded value, because the formula receives the rounded value too.

        With `has_interval_parameters`, the bounds are parameters too, rounded by the same rule, both in the returned
        bounds and at the end of the tuple, where `c_scale` follows them.

        Returns:
            The parameter tuple; the bounds; the exact text of each rounded value; and the parameter values at which
            mpmath evaluates the function, keyed by survey name.
        """
        values, exact_texts_of_rounded_values, mpmath_parameter_values = [], [], {}
        for name, exact_value in published_test_function.parameter_values:
            value, is_rounded = cls._parameter_value(exact_value)
            values.append(value)
            if is_rounded:
                exact_texts_of_rounded_values.append(cls._exact_text(exact_value))
                mpmath_parameter_values[name] = sp.Rational(repr(value))
            else:
                mpmath_parameter_values[name] = exact_value
        interval = published_test_function.interval
        exact_bounds = (sp.sympify(interval.lower), sp.sympify(interval.upper))
        if has_interval_parameters:
            bounds = []
            for exact_bound in exact_bounds:
                bound, is_rounded = cls._parameter_value(exact_bound)
                bounds.append(bound)
                if is_rounded:
                    exact_texts_of_rounded_values.append(cls._exact_text(exact_bound))
            bounds = tuple(bounds)
            values += [*bounds, cls._c_scale(bounds)]
        else:
            bounds = tuple(float(sp.N(bound, 30)) for bound in exact_bounds)
        return tuple(values), bounds, exact_texts_of_rounded_values, mpmath_parameter_values

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_survey(cls, survey_formula: SurveyFormula) -> "FormulaModuleSpec":
        """Build the spec of 1 formula's module from its line of `formulas.csv` and its source's rows.

        Raises:
            GenerationError: If the formula changes its variable, if its function, parameters or intervals cannot be
                read or translated, if a row's function differs from the formula's, or if no case can be found.
        """
        formula_id = survey_formula.formulas_table_line.formula_id
        if survey_formula.formulas_table_line.function_decision.variable_change:
            raise GenerationError(f"{formula_id} changes its variable, which the generator does not support")
        try:
            published_formula = PublishedFormula.from_survey(survey_formula)
            has_interval_parameters = published_formula.has_interval_parameters
            python_names = cls._python_parameter_names(published_formula.survey_parameter_names)
            formula_expression = FormulaExpression.from_text(
                published_formula.f, published_formula.variable, python_names
            )
        except (PublishedTestFunctionsError, TranslationError) as error:
            raise GenerationError(f"{formula_id}: {error}") from error
        param_names = tuple(python_names[name] for name in published_formula.survey_parameter_names)
        if has_interval_parameters:
            param_names += ("a", "b", "c_scale")
        tuples, cases, exact_texts_of_rounded_values = [], [], []
        bounds_cases: dict[tuple[float, float], str] = {}
        for published_test_function in published_formula.test_functions:
            values, bounds, test_function_exact_texts_of_rounded_values, mpmath_parameter_values = cls._tuple_values(
                published_test_function, has_interval_parameters
            )
            if values in tuples:
                # 2 rows, or 2 sets of values of 1 row, can give the same test function; its tuple and cases would only
                # repeat the earlier ones
                continue
            exact_texts_of_rounded_values += test_function_exact_texts_of_rounded_values
            tuples.append(values)
            params = dict(zip(param_names, values, strict=True))
            python_values = {name: value for name, value in params.items() if name in python_names.values()}
            exact_function = formula_expression.mpmath_function(mpmath_parameter_values)
            term_magnitude_function = formula_expression.mpmath_term_magnitude_function(mpmath_parameter_values)
            # the first tuple gets a 2nd value case, which shifts x
            shifts = (0.0, SHIFTED_CASE_C) if not cases else (0.0,)
            shifted_xs = []
            for c in shifts:
                x, expected, atol = cls._find_case(
                    exact_function, term_magnitude_function, formula_expression, python_values, bounds, c=c
                )
                tolerance = f", atol={atol!r}" if atol is not None else ""
                cases.append(
                    f"FormulaTestCase.value(params={params!r}, x={x!r}, c={c!r}, expected={expected!r}{tolerance})"
                )
                shifted_xs.append(x - cls._c_scale(bounds) * c)
            # the first tuple also reaches each branch of a function that is 1 conditional, so that a test reaches
            # every line of the module
            expression_node = ast.parse(formula_expression.python_code, mode="eval").body
            if len(tuples) == 1 and isinstance(expression_node, ast.IfExp):
                namespace = {"math": math, **vars(math_functions), **python_values}
                condition_code = ast.unparse(expression_node.test)
                reached = {bool(eval(condition_code, namespace, {"x": x})) for x in shifted_xs}
                for is_condition_met in {True, False} - reached:
                    branch_case = cls._find_branch_case(
                        exact_function,
                        formula_expression,
                        python_values,
                        bounds,
                        expression_node.test,
                        is_condition_met,
                    )
                    if branch_case is None:
                        raise GenerationError(
                            f"{formula_id}: no case reaches the branch where {condition_code} is {is_condition_met}"
                        )
                    x, expected = branch_case
                    cases.append(f"FormulaTestCase.value(params={params!r}, x={x!r}, c=0.0, expected={expected!r})")
            bounds_cases.setdefault(bounds, f"FormulaTestCase.interval_bounds(params={params!r}, expected={bounds!r})")
        return cls(
            survey_formula=survey_formula,
            formula_expression=formula_expression,
            param_names=param_names,
            renamed_parameters=tuple(
                (name, python_name) for name, python_name in python_names.items() if python_name != name
            ),
            tuples=tuple(tuples),
            interval=None if has_interval_parameters else bounds,
            exact_texts_of_rounded_values=tuple(dict.fromkeys(exact_texts_of_rounded_values)),
            cases=(*cases, *bounds_cases.values()),
        )


# ==================================================================================================
#  Category packages
# ==================================================================================================
def source_category_class_name(source: Source) -> str:
    """Return the class name of a source's category, such as ``DowellJarratt1971``."""
    return _camel_case(slugify(source.short_title))


def formula_names(keys: list[str]) -> list[str]:
    """Return the name of each formula of a source; a formula's module and class are named after the formula's name.

    A formula's key, the key of its first row, may list several locations, separated by `;` or `,`, as a textbook's
    rows do; the formula's `location` keeps them all.

    So that a key of many locations does not make a long name, the name is the key up to the end of its first location.
    While the names of several formulas of the source give module names that differ only in their `fNN` prefix, each
    of those names takes its key's next location too.

    Names can still give module names that differ only in their `fNN` prefix, when their keys have no further location.

    Args:
        keys: The key of each formula of the source, in the order of the formulas.
    """
    # re.split with a group keeps the separators, so that a name is the key's own text: location, separator, location
    locations_and_separators = [re.split(r"([;,])", key) for key in keys]
    n_locations_in_name = [1] * len(keys)
    while True:
        names = [
            "".join(key_parts[: 2 * n - 1]).strip()
            for key_parts, n in zip(locations_and_separators, n_locations_in_name, strict=True)
        ]
        slugs = [slugify(name) for name in names]
        duplicate_slugs = {slug for slug in slugs if slugs.count(slug) > 1}
        extendable_indices = [
            i
            for i, slug in enumerate(slugs)
            if slug in duplicate_slugs and 2 * n_locations_in_name[i] < len(locations_and_separators[i])
        ]
        if extendable_indices:
            for i in extendable_indices:
                n_locations_in_name[i] += 1
        else:
            return names


def source_package_text(source: Source, formulas_table_lines: list[FormulasTableLine], module_names: list[str]) -> str:
    """Return the `__init__.py` of a source's category package, which imports every formula module of the source."""
    class_name = source_category_class_name(source)
    module_docstring = (
        f"This category holds the formulas of {source.short_title}.\n\n{GENERATED_PACKAGE_NOTE.format(kind='package')}"
    )
    class_docstring = f"`{class_name}` is the category of the formulas of 1 publication.\n\n{source.reference}"
    return "\n".join(
        [
            _docstring(module_docstring, width=120),
            "",
            "from sunnbear._core.functions.core import FormulaCategory",
            "",
            f"from . import {', '.join(module_names)}",
            "",
            "",
            f"class {class_name}(FormulaCategory):",
            textwrap.indent(_docstring(class_docstring, width=DOCSTRING_WIDTH), "    "),
            "",
            f"    number = {formulas_table_lines[0].source_number!r}",
            f"    name = {source.short_title!r}",
            "",
        ]
    )


def subcategory_package_text(subcategory: str, source_package_names: list[str]) -> str:
    """Return the `__init__.py` of a subcategory, which imports every source package present in it."""
    description = SUBCATEGORY_DESCRIPTIONS[subcategory]
    name = description[0].upper() + description[1:]
    class_name = _camel_case(slugify(description))
    number = tuple(int(part) for part in subcategory.split("."))
    module_docstring = (
        f"This category holds the formulas of {description}, in 1 subcategory per source.\n\n"
        f"{GENERATED_PACKAGE_NOTE.format(kind='file')}"
    )
    imports = [f"from . import {', '.join(source_package_names)}", ""] if source_package_names else []
    return "\n".join(
        [
            _docstring(module_docstring, width=120),
            "",
            "from sunnbear._core.functions.core import FormulaCategory",
            "",
            *imports,
            "",
            f"class {class_name}(FormulaCategory):",
            f'    """`{class_name}` is subcategory {subcategory} of the published test functions."""',
            "",
            f"    number = {number!r}",
            f"    name = {name!r}",
            "",
        ]
    )


def subcategory_dir(subcategory: str) -> Path:
    """Return the package directory of a subcategory, such as ``c01_articles_of_solvers_that_sunnbear_implements``."""
    number = int(subcategory.split(".")[1])
    return CATALOG_DIR / f"c{number:02d}_{slugify(SUBCATEGORY_DESCRIPTIONS[subcategory])}"


def write_source_package(source: Source, formulas_table_lines: list[FormulasTableLine]) -> list[Path]:
    """Write a source's category package and its generated formula modules, and return the paths written.

    A formula whose module is written by hand (`is_hand_written`) only needs its module to exist.

    Raises:
        GenerationError: If formulas cannot be generated, or hand-written modules are missing; the message names each.
    """
    package_name = f"c{formulas_table_lines[0].source_number[-1]:02d}_{slugify(source.short_title)}"
    package_dir = subcategory_dir(source.subcategory) / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    written, module_names, problems = [], [], []
    survey_formulas = [SurveyFormula(formulas_table_line, source) for formulas_table_line in formulas_table_lines]
    names = formula_names([survey_formula.rows[0].key for survey_formula in survey_formulas])
    for formulas_table_line, survey_formula, formula_name in zip(
        formulas_table_lines, survey_formulas, names, strict=True
    ):
        row = survey_formula.rows[0]
        module_name = f"f{formulas_table_line.number[-1]:02d}_{slugify(formula_name)}"
        path = package_dir / f"{module_name}.py"
        if is_hand_written(survey_formula):
            if not path.exists():
                problems.append(f"{formulas_table_line.formula_id}: its hand-written module {path.name} is missing")
        else:
            try:
                module_spec = FormulaModuleSpec.from_survey(survey_formula)
            except GenerationError as error:
                problems.append(f"{row.row_id}: {error}")
            else:
                path.write_text(module_spec.module_text(formula_name), encoding="utf-8")
                written.append(path)
        module_names.append(module_name)
    if problems:
        raise GenerationError("\n".join(problems))
    else:
        init_path = package_dir / "__init__.py"
        init_path.write_text(source_package_text(source, formulas_table_lines, module_names), encoding="utf-8")
        return [*written, init_path]


def is_hand_written(survey_formula: SurveyFormula) -> bool:
    """Return whether a formula's module is written by hand.

    A formula's module is written by hand when a row has no `f`, or when the formula is in `UNTRANSLATABLE_FORMULAS`.
    """
    has_description = any(row.f_description for row in survey_formula.rows)
    return has_description or survey_formula.formulas_table_line.formula_id in UNTRANSLATABLE_FORMULAS


def write_subcategory_packages() -> list[Path]:
    """Rewrite the `__init__.py` of every subcategory from the source packages present, and return the paths."""
    written = []
    for subcategory in SUBCATEGORY_DESCRIPTIONS:
        directory = subcategory_dir(subcategory)
        directory.mkdir(parents=True, exist_ok=True)
        source_package_names = sorted(path.parent.name for path in directory.glob("c[0-9][0-9]_*/__init__.py"))
        init_path = directory / "__init__.py"
        init_path.write_text(subcategory_package_text(subcategory, source_package_names), encoding="utf-8")
        written.append(init_path)
    return written


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _camel_case(slug: str) -> str:
    """Return a slug in CamelCase, such as ``DowellJarratt1971`` for ``dowell_jarratt_1971``."""
    return "".join(part[:1].upper() + part[1:] for part in slug.split("_"))


def _join_words(words: list[str]) -> str:
    """Return words as an English list, such as ``A``, ``A and B`` or ``A, B and C``."""
    if len(words) == 1:
        return words[0]
    else:
        return f"{', '.join(words[:-1])} and {words[-1]}"


def _docstring(text: str, width: int) -> str:
    """Return `text` as a docstring: each paragraph wrapped at `width`, the opening quotes on its first line.

    In a paragraph, each line from the first line that starts with `- ` onward is a list item, wrapped on its own; the
    lines before that first list item are wrapped together.
    """
    paragraphs = []
    for i, paragraph in enumerate(text.split("\n\n")):
        initial_indent = '"""' if i == 0 else ""
        lines = paragraph.splitlines()
        n_lead_lines = next((k for k, line in enumerate(lines) if line.startswith("- ")), len(lines))
        wrapped = []
        if n_lead_lines:
            wrapped.append(textwrap.fill(" ".join(lines[:n_lead_lines]), width=width, initial_indent=initial_indent))
        wrapped += [textwrap.fill(line, width=width, subsequent_indent="  ") for line in lines[n_lead_lines:]]
        paragraphs.append("\n".join(wrapped))
    if len(paragraphs) == 1 and "\n" not in paragraphs[0] and len(paragraphs[0]) + 3 <= width:
        return paragraphs[0] + '"""'
    else:
        return "\n\n".join(paragraphs) + '\n"""'


def _string_code(text: str, width: int) -> str:
    """Return the code of a string literal, split into implicitly joined pieces of at most `width` characters.

    A piece never spans a line break of `text`, so that the code keeps the text's lines.
    """
    pieces = [
        piece
        for line in text.splitlines(keepends=True)
        for piece in textwrap.wrap(
            line,
            width=width,
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=False,
            break_on_hyphens=False,
        )
    ]
    if "".join(pieces) != text:
        raise GenerationError(f"the text {text!r} does not split into pieces that join back to it")
    elif len(pieces) == 1:
        return repr(text)
    else:
        return "(" + " ".join(repr(piece) for piece in pieces) + ")"


# ==================================================================================================
#  Main
# ==================================================================================================
def main(source_ids: list[str]) -> int:
    """Write the formula modules of the named sources, and return the exit status."""
    folder = DataFolder.in_repo()
    sources = {source.source_id: source for source in read_sources(folder.sources_dir)}
    formulas_table = FormulasTable.read(folder.formulas_file)
    written: list[Path] = []
    problems: list[str] = []
    for source_id in source_ids:
        formulas_table_lines = [
            line for line in formulas_table.formulas if line.source_id == source_id and not line.is_retired
        ]
        if source_id not in sources or not formulas_table_lines:
            problems.append(f"{source_id} is no source with active formulas")
            continue
        try:
            written += write_source_package(sources[source_id], formulas_table_lines)
        except GenerationError as error:
            problems += str(error).splitlines()
    for problem in problems:
        print(f"problem: {problem}")
    if problems:
        return 1
    else:
        written += write_subcategory_packages()
        paths = [str(path) for path in written]
        # formatting first shortens the long lines, so that `check --fix`, which sorts the imports, reports only real
        # problems
        subprocess.run([sys.executable, "-m", "ruff", "format", "--quiet", *paths], check=True)
        subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", "--quiet", *paths], check=False)
        subprocess.run([sys.executable, "-m", "ruff", "format", "--quiet", *paths], check=True)
        print(f"wrote {len(written)} files")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
