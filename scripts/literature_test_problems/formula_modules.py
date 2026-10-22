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

import hashlib
import itertools
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

from sunnbear._core.utils.slugify import slugify
from sunnbear.functions import CANONICAL_DIGITS, ParamNotation

from .data_files import SUBCATEGORY_DESCRIPTIONS, DataFileError, DataFolder, Source, SourceRow, read_sources
from .formulas import FormulasTable, FormulasTableLine
from .functions import ParsedFunction
from .helpers import IDENTIFIER, MAX_INSTANCES
from .intervals import ParsedIntervals

CATALOG_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "sunnbear" / "_core" / "functions" / "catalog"
) / "c01_published_test_functions"
# fmt: off
# PYTHON_FUNCTIONS maps each function name of the survey that the generator supports to its Python form.
PYTHON_FUNCTIONS = {
    "exp": "math.exp", "sin": "math.sin", "cos": "math.cos", "tan": "math.tan",
    "asin": "math.asin", "acos": "math.acos", "atan": "math.atan",
    "arcsin": "math.asin", "arccos": "math.acos", "arctan": "math.atan",
    "sinh": "math.sinh", "cosh": "math.cosh", "tanh": "math.tanh",
    "asinh": "math.asinh", "acosh": "math.acosh", "atanh": "math.atanh",
    "log": "math.log", "ln": "math.log", "log10": "math.log10", "log2": "math.log2",
    "sqrt": "math.sqrt", "abs": "abs", "floor": "math.floor", "ceil": "math.ceil", "ceiling": "math.ceil",
    "erf": "math.erf", "erfc": "math.erfc", "gamma": "math.gamma", "Gamma": "math.gamma",
    "max": "max", "min": "min", "atan2": "math.atan2",
}
# fmt: on
# PYTHON_CONSTANTS maps each constant of the survey to its Python form; `e` is a constant unless a parameter has its
# name.
PYTHON_CONSTANTS = {"pi": "math.pi", "e": "math.e"}
# CASE_FRACTIONS are the positions in the interval, as fractions of its width, at which the cases are tried, in
# order; the first position where the generated Python agrees with mpmath is kept.
CASE_FRACTIONS = (0.3, 0.7, 0.45, 0.85, 0.6, 0.35)
# CASE_SHIFT is the value of c of the 1 case per formula that exercises the shift of x.
CASE_SHIFT = 0.25
# CASE_RTOL and CASE_ATOL bound how far the generated Python may be from mpmath at a case's x-value: 10 times smaller
# than the default tolerances of the generic formula test, so that the numba-compiled function, whose result may
# differ slightly from the Python one, still passes that test.
CASE_RTOL = 1e-13
CASE_ATOL = 1e-13
# DOCSTRING_WIDTH is the width of a wrapped docstring line, inside a class at 4 spaces of indentation.
DOCSTRING_WIDTH = 120 - 4
# RESERVED_NAMES are the names that a parameter of the source may not keep, because the formula module uses them.
RESERVED_NAMES = {"x", "c", "self", "math"}
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
        param_names: The Python names of the formula's parameters, in tuple order; a formula with several
            intervals ends them with `a` and `b`.
        interval: The single interval of a formula that has 1, and None otherwise.
        exact_texts_of_rounded_bounds: The exact text of each bound that the tuples round to `CANONICAL_DIGITS`
            significant digits.
        cases: Each case as the Python code of a `FormulaTestCase` factory call.
    """

    formulas_table_line: FormulasTableLine
    source: Source
    row: SourceRow
    param_names: tuple[str, ...]
    expression_code: str
    tuples: tuple[tuple[float, ...], ...]
    interval: tuple[float, float] | None
    exact_texts_of_rounded_bounds: tuple[str, ...]
    cases: tuple[str, ...]

    def module_text(self) -> str:
        """Return the formula's module as Python source, before ruff formats it."""
        command = f"uv run python -m scripts.literature_test_problems.formula_modules {self.source.source_id}"
        module_docstring = (
            f"This module holds the formula of {self.row.key} in {self.source.short_title}.\n\n"
            "A script generates this module from the survey of published test problems: to change the formula, change "
            f"its source file in `data/literature_test_problems/sources/` and run `{command}`, never this file."
        )
        needs_math_import = "math." in self.expression_code
        needs_param_table_import = bool(self.param_names)
        imported_names = ["Formula", "FormulaSource", "FormulaTestCase", "ParamRecipe"]
        if needs_param_table_import:
            imported_names.append("ParamTable")
        if self.interval is None:
            interval_width_code = "(b - a)"
        else:
            interval_width_code = repr(self.interval[1] - self.interval[0])
        class_name = source_category_class_name(self.source) + _camel_case(slugify(self.row.key))
        signature = "".join(f", {name}: float" for name in self.param_names)
        return "\n".join(
            [
                _docstring(module_docstring, width=120),
                "",
                *(["import math", ""] if needs_math_import else []),
                f"from sunnbear._core.functions.core import {', '.join(imported_names)}",
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
                f"    name = {self.row.key!r}",
                f"    param_names = {self.param_names!r}",
                "    source = FormulaSource(",
                f"        reference={_string_code(self.source.reference, width=90)},",
                f"        location={self.row.key!r},",
                "    )",
                "",
                "    @staticmethod",
                f"    def parametrized_fun(x: float, c: float{signature}) -> float:",
                '        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula\'s '
                'interval."""',
                f"        x = x - {interval_width_code} * c",
                f"        return {self.expression_code}",
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
        if source.source_id != formulas_table_line.source_id:
            raise DataFileError(f"{formulas_table_line.formula_id}: {source.source_id} is not its source")
        fields = [
            source.title,
            source.reference,
            formulas_table_line.variable_change,
            [
                [row.row_id, row.f, row.f_description, row.parameters, row.interval, row.notes]
                for row in (source.find_row(row_id) for row_id in formulas_table_line.row_ids)
            ],
        ]
        return hashlib.sha256(json.dumps(fields).encode("utf-8")).hexdigest()[:16]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _class_docstring(self) -> str:
        """Return the class docstring: what the formula evaluates, the row's values, rounded bounds and notes."""
        paragraphs = [
            "This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval."
        ]
        interval_text = self.row.interval.strip()
        if "`" not in interval_text:
            interval_text = f"``{interval_text}``"
        # the survey's interval may be the span between a source's 2 starting values, so the docstring does not claim
        # that the source prints the interval
        if self.row.parameters.strip():
            paragraphs.append(
                f"The source prints ``{self.row.f}``, with the parameters ``{self.row.parameters.strip()}``; the "
                f"formula's interval is {interval_text}."
            )
        else:
            paragraphs.append(f"The source prints ``{self.row.f}``; the formula's interval is {interval_text}.")
        if self.exact_texts_of_rounded_bounds:
            paragraphs.append(
                f"The bounds {', '.join(f'``{bound}``' for bound in self.exact_texts_of_rounded_bounds)} are rounded "
                f"to {CANONICAL_DIGITS} significant digits, the most that a parameter value holds."
            )
        if self.row.notes.strip():
            paragraphs.append(self.row.notes.strip())
        return "\n\n".join(paragraphs)

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
    def _python_expression_code(text: str, variable: str, parameter_names: dict[str, str]) -> str:
        """Translate the survey's expression text into Python code that numba compiles, keeping its operation order.

        An equation `lhs = rhs` becomes `(lhs) - (rhs)`, `^` becomes `**`, the variable becomes `x`, and each
        function and constant takes its Python form (`PYTHON_FUNCTIONS`, `PYTHON_CONSTANTS`).

        Args:
            text: The row's `f`.
            variable: The name of the row's unknown.
            parameter_names: The Python name of each parameter of the row, keyed by its name in the survey.

        Raises:
            GenerationError: If the text names a function or a name that the translation does not know, or the
                result is not a Python expression.
        """
        sides = text.split("=")
        if len(sides) == 2:
            text = f"({sides[0].strip()}) - ({sides[1].strip()})"
        text = text.replace("^", "**")

        def to_python(match: re.Match) -> str:
            """Return the Python form of 1 name of the expression."""
            name = match.group(1)
            is_call = text[match.end() :].lstrip().startswith("(")
            if is_call and name in PYTHON_FUNCTIONS:
                return PYTHON_FUNCTIONS[name]
            elif is_call:
                raise GenerationError(f"the function {name} has no Python form in the generator")
            elif name == variable:
                return "x"
            elif name in parameter_names:
                return parameter_names[name]
            elif name in PYTHON_CONSTANTS:
                return PYTHON_CONSTANTS[name]
            else:
                raise GenerationError(f"the name {name} is neither the variable, a parameter nor a constant")

        code = IDENTIFIER.sub(to_python, text)
        try:
            compile(code, "<expression>", "eval")
        except SyntaxError as error:
            raise GenerationError(f"the Python form {code!r} does not compile") from error
        return code

    @staticmethod
    def _python_parameter_names(survey_names: list[str], has_interval_parameters: bool) -> dict[str, str]:
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
    def _find_case_x_and_expected(
        exact_expression: sp.Expr,
        variable: sp.Symbol,
        expression_code: str,
        python_values: dict[str, float],
        interval: tuple[float, float],
        c: float,
    ) -> tuple[float, float]:
        """Return an x-value in the interval and the formula's value there, where the Python agrees with mpmath.

        The x-values tried are `CASE_FRACTIONS` of the interval, rounded to 6 significant digits. The Python and
        mpmath both evaluate the expression at the float `x - (b - a)*c`, computed as the generated code computes it,
        so that only the expression's own arithmetic can differ.

        Raises:
            GenerationError: If the Python agrees with mpmath at none of the x-values tried.
        """
        a, b = interval
        exact_function = sp.lambdify(variable, exact_expression, modules="mpmath")
        for fraction in CASE_FRACTIONS:
            x = float(f"{a + fraction * (b - a):.6g}")
            shifted = x - (b - a) * c
            if not a < x < b:
                continue
            try:
                with mpmath.workdps(50):
                    exact_value = mpmath.mpmathify(exact_function(mpmath.mpf(shifted)))
                python_value = eval(expression_code, {"math": math}, {**python_values, "x": shifted})
            except (ArithmeticError, ValueError, TypeError):
                continue
            if isinstance(exact_value, mpmath.mpc) or not isinstance(python_value, float):
                continue
            expected = float(exact_value)
            if math.isfinite(expected) and math.isclose(python_value, expected, rel_tol=CASE_RTOL, abs_tol=CASE_ATOL):
                return x, expected
        raise GenerationError(f"the Python form agrees with mpmath at none of the x-values tried, c = {c}")

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_survey(cls, formulas_table_line: FormulasTableLine, source: Source) -> "FormulaModuleSpec":
        """Build the spec of 1 formula's module from its line of `formulas.csv` and its source's row.

        Raises:
            GenerationError: If the formula holds several rows, changes its variable, or has parameters that give
                several sets of values, or if its expression, parameters or intervals cannot be translated.
        """
        formula_id = formulas_table_line.formula_id
        if len(formulas_table_line.row_ids) > 1:
            raise GenerationError(f"{formula_id} holds several rows, which the generator does not support")
        elif formulas_table_line.variable_change:
            raise GenerationError(f"{formula_id} changes its variable, which the generator does not support")
        row = source.find_row(formulas_table_line.row_ids[0])
        # --- parse the row ----------------------
        if ParsedFunction.from_source_row(row).has_value_sets:
            raise GenerationError(f"{formula_id}: its parameters give several sets of values")
        expr, variable, survey_parameters = ParsedFunction.parse_row_expression(row)
        survey_names = [name for name in survey_parameters if sp.Symbol(name) in expr.free_symbols]
        combos = list(itertools.product(*(survey_parameters[name] for name in survey_names)))
        if len(combos) > MAX_INSTANCES:
            raise GenerationError(f"{formula_id}: more than {MAX_INSTANCES} parameter combinations")
        intervals = ParsedIntervals.from_source_row(row).intervals
        pairs = [
            (combo, interval)
            for combo in combos
            for interval in intervals
            if interval.matches_parameter_values(tuple(zip(survey_names, combo, strict=True)))
        ]
        if not pairs:
            raise GenerationError(f"{formula_id}: no instance has a usable interval")
        # --- the formula's parameters -----------
        has_interval_parameters = len({interval.key for _, interval in pairs}) > 1
        python_names = cls._python_parameter_names(survey_names, has_interval_parameters)
        expression_code = cls._python_expression_code(row.f, variable.name, python_names)
        param_names = tuple(python_names[name] for name in survey_names)
        if has_interval_parameters:
            param_names += ("a", "b")
        tuples, cases, exact_texts_of_rounded_bounds = [], [], []
        bounds_cases: dict[tuple[float, float], str] = {}
        for combo, interval in pairs:
            values = tuple(cls._parameter_value(value, name) for name, value in zip(survey_names, combo, strict=True))
            exact_bounds = (sp.sympify(interval.lower), sp.sympify(interval.upper))
            bounds = tuple(float(sp.N(bound, 30)) for bound in exact_bounds)
            if has_interval_parameters:
                rounded = tuple(float(f"{bound:.{CANONICAL_DIGITS}g}") for bound in bounds)
                exact_texts_of_rounded_bounds += [
                    str(e) for e, r, f in zip(exact_bounds, rounded, bounds, strict=True) if r != f
                ]
                bounds = rounded
                values += bounds
            tuples.append(values)
            params = dict(zip(param_names, values, strict=True))
            python_values = {name: value for name, value in params.items() if name in python_names.values()}
            exact_expression = expr.subs(dict(zip((sp.Symbol(name) for name in survey_names), combo, strict=True)))
            # the first tuple gets a 2nd value case, which shifts x
            shifts = (0.0, CASE_SHIFT) if not cases else (0.0,)
            for c in shifts:
                x, expected = cls._find_case_x_and_expected(
                    exact_expression, variable, expression_code, python_values, bounds, c=c
                )
                cases.append(f"FormulaTestCase.value(params={params!r}, x={x!r}, c={c!r}, expected={expected!r})")
            bounds_cases.setdefault(bounds, f"FormulaTestCase.interval_bounds(params={params!r}, expected={bounds!r})")
        return cls(
            formulas_table_line=formulas_table_line,
            source=source,
            row=row,
            param_names=param_names,
            expression_code=expression_code,
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

    Raises:
        GenerationError: If a formula cannot be generated, or a hand-written module is missing.
    """
    package_name = f"c{formulas_table_lines[0].source_number[-1]:02d}_{slugify(source.short_title)}"
    package_dir = subcategory_dir(source.subcategory) / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    written, module_names = [], []
    for formulas_table_line in formulas_table_lines:
        row = source.find_row(formulas_table_line.row_ids[0])
        module_name = f"f{formulas_table_line.number[-1]:02d}_{slugify(row.key)}"
        if row.f_description:
            if not (package_dir / f"{module_name}.py").exists():
                raise GenerationError(
                    f"{formulas_table_line.formula_id}: its hand-written module {module_name}.py is missing"
                )
        else:
            try:
                module_spec = FormulaModuleSpec.from_survey(formulas_table_line, source)
            except GenerationError as error:
                raise GenerationError(f"{formulas_table_line.formula_id} ({row.row_id}): {error}") from error
            path = package_dir / f"{module_name}.py"
            path.write_text(module_spec.module_text(), encoding="utf-8")
            written.append(path)
        module_names.append(module_name)
    init_path = package_dir / "__init__.py"
    init_path.write_text(source_package_text(source, formulas_table_lines, module_names), encoding="utf-8")
    return [*written, init_path]


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
    for source_id in source_ids:
        formulas_table_lines = [
            line for line in formulas_table.formulas if line.source_id == source_id and not line.is_retired
        ]
        if source_id not in sources or not formulas_table_lines:
            print(f"problem: {source_id} is no source with active formulas")
            return 1
        try:
            written += write_source_package(sources[source_id], formulas_table_lines)
        except GenerationError as error:
            print(f"problem: {error}")
            return 1
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
