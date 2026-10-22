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
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import mpmath
import sympy as sp

from sunnbear._core.utils import math_functions
from sunnbear._core.utils.slugify import slugify
from sunnbear.functions import CANONICAL_DIGITS, ParamNotation

from .data_files import SUBCATEGORY_DESCRIPTIONS, DataFolder, Source, SourceRow, read_sources
from .formula_expressions import FormulaExpression, TranslationError
from .formulas import FormulasTable, FormulasTableLine
from .published_cases import PublishedCase, PublishedCasesError, PublishedFormula

CATALOG_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "sunnbear" / "_core" / "functions" / "catalog"
) / "c01_published_test_functions"
# HAND_WRITTEN_FORMULAS holds, with the reason, each formula whose rows give an `f` that the script cannot translate,
# and whose module is therefore written by hand.
HAND_WRITTEN_FORMULAS = {
    "f1.1.2.4": "an infinite sum, which the module sums until its terms vanish in float64",
    "f1.1.11.2": "a function `alpha` that the row's parameters define",
}
# CASE_FRACTIONS are the positions in the interval, as fractions of its width, at which the cases are tried, in
# order; the first position where the generated Python agrees with mpmath is kept. All are at least `CASE_SHIFT`, so
# that the shifted x-value of a case stays in the interval.
CASE_FRACTIONS = (0.3, 0.7, 0.45, 0.85, 0.6, 0.35)
# CASE_SHIFT is the value of c of the 1 case per formula that exercises the shift of x.
CASE_SHIFT = 0.25
# CASE_RTOL and CASE_ATOL bound how far the generated Python may be from mpmath at a case's x-value: 10 times smaller
# than the default tolerances of the generic formula test, so that the numba-compiled function, whose result may
# differ slightly from the Python one, still passes that test.
CASE_RTOL = 1e-13
CASE_ATOL = 1e-13
# CASE_X_ULPS is the number of float64 steps of x, on each side of a case's x-value, over which
# `FormulaModuleSpec._find_case` measures the spread of the function's exact values.
CASE_X_ULPS = 4
# DOCSTRING_WIDTH is the width of a wrapped docstring line, inside a class at 4 spaces of indentation.
DOCSTRING_WIDTH = 120 - 4
# RESERVED_NAMES are the names that a parameter of the source may not keep, because the formula module uses them.
RESERVED_NAMES = {"x", "c", "self", "math", *math_functions.__all__}
# GENERATED_PACKAGE_NOTE ends the module docstring of each generated package's `__init__.py`.
GENERATED_PACKAGE_NOTE = (
    "A script generates this {kind} from the survey of published test problems: to change it, change the survey and "
    "run `scripts/literature_test_problems/formula_modules.py`, never this file."
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
        expression: The formula's function as Python code and as a sympy expression.
        param_names: The Python names of the formula's parameters, in tuple order; a formula with several
            intervals ends them with `a` and `b`.
        interval: The single interval of a formula that has 1, and None otherwise.
        exact_texts_of_rounded_bounds: The exact text of each bound that the tuples round to `CANONICAL_DIGITS`
            significant digits.
        cases: Each case as the Python code of a `FormulaTestCase` factory call.
    """

    formulas_table_line: FormulasTableLine
    source: Source
    expression: FormulaExpression
    param_names: tuple[str, ...]
    tuples: tuple[tuple[float, ...], ...]
    interval: tuple[float, float] | None
    exact_texts_of_rounded_bounds: tuple[str, ...]
    cases: tuple[str, ...]

    @property
    def rows(self) -> tuple[SourceRow, ...]:
        """Return the formula's rows, in the order of `formulas.csv`."""
        return self.formulas_table_line.rows(self.source)

    def module_text(self) -> str:
        """Return the formula's module as Python source, before ruff formats it."""
        location = ", ".join(row.key for row in self.rows)
        command = f"uv run python -m scripts.literature_test_problems.formula_modules {self.source.source_id}"
        module_docstring = (
            f"This module holds the formula of {location} in {self.source.short_title}.\n\n"
            "A script generates this module from the survey of published test problems: to change the formula, change "
            f"its source file in `data/literature_test_problems/sources/` and run `{command}`, never this file."
        )
        needs_math_import = "math." in self.expression.python_code
        helper_functions = self.expression.helper_functions
        imported_names = ["Formula", "FormulaSource", "FormulaTestCase", "ParamRecipe"]
        if self.param_names:
            imported_names.append("ParamTable")
        if self.interval is None:
            interval_width_code = "(b - a)"
        else:
            interval_width_code = repr(self.interval[1] - self.interval[0])
        class_name = source_category_class_name(self.source) + _camel_case(slugify(self.rows[0].key))
        signature = "".join(f", {name}: float" for name in self.param_names)
        return "\n".join(
            [
                _docstring(module_docstring, width=120),
                "",
                *(["import math", ""] if needs_math_import else []),
                f"from sunnbear._core.functions.core import {', '.join(imported_names)}",
                *(
                    [f"from sunnbear._core.utils.math_functions import {', '.join(helper_functions)}"]
                    if helper_functions
                    else []
                ),
                "",
                "# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the",
                "# survey, so that a test fails when the survey changes and this module is not regenerated.",
                f'SURVEY_FIELDS_HASH = "{self.survey_fields_hash(self.formulas_table_line, self.source)}"',
                "",
                "",
                f"class {class_name}(Formula):",
                textwrap.indent(_docstring(self._class_docstring(), width=DOCSTRING_WIDTH), "    "),
                "",
                f"    number = {self.formulas_table_line.number!r}",
                f"    name = {self.rows[0].key!r}",
                f"    param_names = {self.param_names!r}",
                "    source = FormulaSource(",
                f"        reference={_string_code(self.source.reference, width=90)},",
                f"        location={location!r},",
                "    )",
                "",
                "    @staticmethod",
                f"    def parametrized_fun(x: float, c: float{signature}) -> float:",
                '        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula\'s '
                'interval."""',
                *self._parametrized_fun_body(interval_width_code),
                "",
                f"    def interval_bounds(self{signature}) -> tuple[float, float]:",
                *self._interval_bounds_body(),
                "",
                "    def recipes(self) -> tuple[ParamRecipe, ...]:",
                *self._recipes_body(),
                "",
                "    cases = (",
                *(f"        {case}," for case in self.cases),
                "    )",
                "",
            ]
        )

    @staticmethod
    def survey_fields_hash(formulas_table_line: FormulasTableLine, source: Source) -> str:
        """Return a hash of the formula's survey fields: every field of the survey that its generated module depends on.

        The tests recompute the hash and compare it with the module's `SURVEY_FIELDS_HASH`, so that a module left stale
        after a change of the survey fails them. A row's id holds its key, so the hash covers the key too.

        Raises:
            DataFileError: If `source` is not the formula's source, or lacks 1 of the formula's rows.
        """
        function_decision = formulas_table_line.function_decision
        fields = [
            source.title,
            source.reference,
            [function_decision.variable_change, function_decision.f, function_decision.parameters],
            [
                [row.row_id, row.f, row.f_description, row.parameters, row.interval, row.notes]
                for row in formulas_table_line.rows(source)
            ],
        ]
        return hashlib.sha256(json.dumps(fields).encode("utf-8")).hexdigest()[:16]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _class_docstring(self) -> str:
        """Return the class docstring: what the formula evaluates, the rows' functions and values, and their notes."""
        paragraphs = [
            "This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval."
        ]
        # the survey's interval may be the span between a source's 2 starting values, so the docstring does not claim
        # that the source prints the interval
        if len(self.rows) == 1:
            paragraphs.append(f"The source prints {self._row_text(self.rows[0])}.")
        else:
            function_decision = self.formulas_table_line.function_decision
            if function_decision.f:
                paragraphs.append(
                    f"The source prints 1 function in {len(self.rows)} rows, each with its own parameter values; the "
                    f"formula writes that function as ``{function_decision.f}``:"
                )
            else:
                paragraphs.append(f"The source prints 1 function in {len(self.rows)} rows, each on its own interval:")
            values_per_row = function_decision.values_per_row() or [""] * len(self.rows)
            paragraphs.append(
                "\n".join(
                    f"- {row.key}" + (f", with ``{values}``" if values else "") + f": {self._row_text(row)}"
                    for row, values in zip(self.rows, values_per_row, strict=True)
                )
            )
        if self.exact_texts_of_rounded_bounds:
            paragraphs.append(
                f"The bounds {', '.join(f'``{bound}``' for bound in self.exact_texts_of_rounded_bounds)} are rounded "
                f"to {CANONICAL_DIGITS} significant digits, the most that a parameter value holds."
            )
        for row in self.rows:
            if row.notes.strip() and len(self.rows) == 1:
                paragraphs.append(row.notes.strip())
            elif row.notes.strip():
                paragraphs.append(f"{row.key}: {row.notes.strip()}")
        return "\n\n".join(paragraphs)

    @staticmethod
    def _row_text(row: SourceRow) -> str:
        """Return a row's function, its parameters and its interval, as the docstring states them."""
        interval_text = row.interval.strip()
        if "`" not in interval_text:
            interval_text = f"``{interval_text}``"
        if row.parameters.strip():
            return (
                f"``{row.f}``, with the parameters ``{row.parameters.strip()}``; the formula's interval is "
                f"{interval_text}"
            )
        else:
            return f"``{row.f}``; the formula's interval is {interval_text}"

    def _parametrized_fun_body(self, interval_width_code: str) -> list[str]:
        """Return the lines of `parametrized_fun` after its docstring: the shift of x, then the function's value.

        The lines differ for 2 forms of the function:

        - when the published function is `x` itself, the method returns the shifted x directly, because assigning x
          only to return it breaks ruff's rule RET504;
        - when the whole Python expression is a conditional `a if condition else b`, the method writes it as an `if`
          statement with a `return` in each branch, so that each branch stands on its own line. A conditional
          inside a larger expression stays an expression, because the published `if(...)` is part of that expression.
        """
        expression_node = ast.parse(self.expression.python_code, mode="eval").body
        if self.expression.python_code.strip() == "x":
            return [f"        return x - {interval_width_code} * c"]
        elif isinstance(expression_node, ast.IfExp):
            return [
                f"        x = x - {interval_width_code} * c",
                f"        if {ast.unparse(expression_node.test)}:",
                f"            return {ast.unparse(expression_node.body)}",
                "        else:",
                f"            return {ast.unparse(expression_node.orelse)}",
            ]
        else:
            return [f"        x = x - {interval_width_code} * c", f"        return {self.expression.python_code}"]

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
            tuples_code = ", ".join(
                f"({', '.join(repr(value) for value in param_tuple)},)" for param_tuple in self.tuples
            )
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
    def _python_parameter_names(survey_names: tuple[str, ...], has_interval_parameters: bool) -> dict[str, str]:
        """Return the Python name of each survey parameter: its own name, with `_` added where Python needs it."""
        reserved = RESERVED_NAMES | ({"a", "b"} if has_interval_parameters else set())
        python_names = {}
        for name in survey_names:
            python_name = name
            while python_name in reserved or keyword.iskeyword(python_name):
                python_name += "_"
            python_names[name] = python_name
        return python_names

    @staticmethod
    def _parameter_value(value: sp.Expr, name: str) -> float:
        """Return a published parameter value as a float, or raise `GenerationError` if no parameter can hold it."""
        number = float(sp.N(value, 30))
        if not ParamNotation.is_valid_value(number):
            raise GenerationError(f"{name} = {value} needs more than {CANONICAL_DIGITS} significant digits")
        return number

    @staticmethod
    def _find_case(
        exact_function: object,
        python_code: str,
        python_values: dict[str, float],
        interval: tuple[float, float],
        c: float,
    ) -> tuple[float, float, float | None]:
        """Return an x-value in the interval, the formula's value there, and the `atol` that the case needs, if any.

        The x-values tried are `CASE_FRACTIONS` of the interval, rounded to 6 significant digits. The Python and
        mpmath both evaluate the function at the float `x - (b - a)*c`, computed as the generated code computes it,
        so that only the function's own arithmetic can differ. The first x-value where they agree within `CASE_RTOL`
        and `CASE_ATOL` is kept; failing that, the first where they differ by no more than the function's spread over
        `CASE_X_ULPS` float64 steps of x, with an `atol` of 10 times that spread, since float64 arithmetic cannot do
        better there.

        Raises:
            GenerationError: If the function is complex at an x-value tried, or the Python agrees with mpmath at none.
        """
        a, b = interval
        fallback_case = None
        for fraction in CASE_FRACTIONS:
            x = float(f"{a + fraction * (b - a):.6g}")
            shifted = x - (b - a) * c
            if not a < x < b:
                continue
            try:
                with mpmath.workdps(50):
                    exact_value = mpmath.mpmathify(exact_function(mpmath.mpf(shifted)))
                python_value = eval(
                    python_code, {"math": math, **vars(math_functions)}, {**python_values, "x": shifted}
                )
            except (ArithmeticError, ValueError, TypeError):
                continue
            if isinstance(exact_value, mpmath.mpc) and abs(exact_value.imag) > 1e-30 * abs(exact_value):
                raise GenerationError(f"the function is complex at x = {shifted!r}")
            expected = float(mpmath.re(exact_value))
            if not math.isfinite(expected) or not isinstance(python_value, float):
                continue
            if math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=CASE_ATOL):
                return x, expected, None
            elif fallback_case is None:
                spread = FormulaModuleSpec._value_spread(exact_function, shifted, expected)
                if abs(python_value - expected) <= spread:
                    fallback_case = (x, expected, float(f"{10 * spread:.1g}"))
        if fallback_case is not None:
            return fallback_case
        else:
            raise GenerationError(f"the Python form agrees with mpmath at none of the x-values tried, c = {c}")

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

    @classmethod
    def _tuple_values(
        cls, published_case: PublishedCase, has_interval_parameters: bool
    ) -> tuple[tuple[float, ...], tuple[float, float], list[str]]:
        """Return a case's parameter tuple, its interval's bounds, and the exact text of each bound that it rounds.

        With `has_interval_parameters`, the tuple ends with the bounds, rounded to `CANONICAL_DIGITS` significant
        digits.
        """
        values = tuple(cls._parameter_value(value, name) for name, value in published_case.parameter_values)
        exact_bounds = (sp.sympify(published_case.interval.lower), sp.sympify(published_case.interval.upper))
        bounds = tuple(float(sp.N(bound, 30)) for bound in exact_bounds)
        exact_texts_of_rounded_bounds = []
        if has_interval_parameters:
            rounded = tuple(float(f"{bound:.{CANONICAL_DIGITS}g}") for bound in bounds)
            exact_texts_of_rounded_bounds = [
                str(e) for e, r, f in zip(exact_bounds, rounded, bounds, strict=True) if r != f
            ]
            bounds = rounded
            values += bounds
        return values, bounds, exact_texts_of_rounded_bounds

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_survey(cls, formulas_table_line: FormulasTableLine, source: Source) -> "FormulaModuleSpec":
        """Build the spec of 1 formula's module from its line of `formulas.csv` and its source's rows.

        Raises:
            GenerationError: If the formula changes its variable, if its function, parameters or intervals cannot be
                read or translated, if a row's function differs from the formula's, or if no case can be found.
        """
        formula_id = formulas_table_line.formula_id
        if formulas_table_line.function_decision.variable_change:
            raise GenerationError(f"{formula_id} changes its variable, which the generator does not support")
        try:
            published_formula = PublishedFormula.from_survey(formulas_table_line, source)
            has_interval_parameters = published_formula.has_interval_parameters
            python_names = cls._python_parameter_names(published_formula.parameter_names, has_interval_parameters)
            expression = FormulaExpression.from_text(published_formula.f, published_formula.variable, python_names)
        except (PublishedCasesError, TranslationError) as error:
            raise GenerationError(f"{formula_id}: {error}") from error
        param_names = tuple(python_names[name] for name in published_formula.parameter_names)
        if has_interval_parameters:
            param_names += ("a", "b")
        tuples, cases, exact_texts_of_rounded_bounds = [], [], []
        bounds_cases: dict[tuple[float, float], str] = {}
        for published_case in published_formula.cases:
            values, bounds, case_exact_texts_of_rounded_bounds = cls._tuple_values(
                published_case, has_interval_parameters
            )
            exact_texts_of_rounded_bounds += case_exact_texts_of_rounded_bounds
            tuples.append(values)
            params = dict(zip(param_names, values, strict=True))
            python_values = {name: value for name, value in params.items() if name in python_names.values()}
            exact_function = expression.mpmath_function(dict(published_case.parameter_values))
            # the first tuple gets a 2nd value case, which shifts x
            shifts = (0.0, CASE_SHIFT) if not cases else (0.0,)
            for c in shifts:
                x, expected, atol = cls._find_case(exact_function, expression.python_code, python_values, bounds, c=c)
                tolerance = f", atol={atol!r}" if atol is not None else ""
                cases.append(
                    f"FormulaTestCase.value(params={params!r}, x={x!r}, c={c!r}, expected={expected!r}{tolerance})"
                )
            bounds_cases.setdefault(bounds, f"FormulaTestCase.interval_bounds(params={params!r}, expected={bounds!r})")
        return cls(
            formulas_table_line=formulas_table_line,
            source=source,
            expression=expression,
            param_names=param_names,
            tuples=tuple(tuples),
            interval=None if has_interval_parameters else bounds,
            exact_texts_of_rounded_bounds=tuple(dict.fromkeys(exact_texts_of_rounded_bounds)),
            cases=(*cases, *bounds_cases.values()),
        )


# ==================================================================================================
#  Category packages
# ==================================================================================================
def source_category_class_name(source: Source) -> str:
    """Return the class name of a source's category, such as ``DowellJarratt1971``."""
    return _camel_case(slugify(source.short_title))


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
    for formulas_table_line in formulas_table_lines:
        row = source.find_row(formulas_table_line.row_ids[0])
        module_name = f"f{formulas_table_line.number[-1]:02d}_{slugify(row.key)}"
        path = package_dir / f"{module_name}.py"
        if is_hand_written(formulas_table_line, source):
            if not path.exists():
                problems.append(f"{formulas_table_line.formula_id}: its hand-written module {path.name} is missing")
        else:
            try:
                module_spec = FormulaModuleSpec.from_survey(formulas_table_line, source)
            except GenerationError as error:
                problems.append(f"{row.row_id}: {error}")
            else:
                path.write_text(module_spec.module_text(), encoding="utf-8")
                written.append(path)
        module_names.append(module_name)
    if problems:
        raise GenerationError("\n".join(problems))
    init_path = package_dir / "__init__.py"
    init_path.write_text(source_package_text(source, formulas_table_lines, module_names), encoding="utf-8")
    return [*written, init_path]


def is_hand_written(formulas_table_line: FormulasTableLine, source: Source) -> bool:
    """Return whether a formula's module is written by hand.

    A formula's module is written by hand when a row of the formula gives only an `f_description`, or when the formula
    is 1 of `HAND_WRITTEN_FORMULAS`.
    """
    has_description = any(row.f_description for row in formulas_table_line.rows(source))
    return has_description or formulas_table_line.formula_id in HAND_WRITTEN_FORMULAS


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


def _docstring(text: str, width: int) -> str:
    """Return `text` as a docstring: each paragraph wrapped at `width`, the opening quotes on its first line.

    A paragraph whose lines all start with `- ` is a list, whose items are wrapped one by one.
    """
    paragraphs = []
    for i, paragraph in enumerate(text.split("\n\n")):
        initial_indent = '"""' if i == 0 else ""
        lines = paragraph.splitlines()
        if all(line.startswith("- ") for line in lines):
            paragraphs.append("\n".join(textwrap.fill(line, width=width, subsequent_indent="  ") for line in lines))
        else:
            paragraphs.append(textwrap.fill(paragraph, width=width, initial_indent=initial_indent))
    if len(paragraphs) == 1 and "\n" not in paragraphs[0] and len(paragraphs[0]) + 3 <= width:
        return paragraphs[0] + '"""'
    else:
        return "\n\n".join(paragraphs) + '\n"""'


def _string_code(text: str, width: int) -> str:
    """Return the code of a string literal, split into implicitly joined pieces of at most `width` characters."""
    pieces = textwrap.wrap(text, width=width, drop_whitespace=False, break_long_words=False, break_on_hyphens=False)
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
