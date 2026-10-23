"""This module reads 1 formula from the survey: its function and its published test functions.

A published test function is 1 combination of the formula's parameter values, on 1 interval. A formula's function is
the `f` of its first row, unless the formula's line in `formulas.csv` gives an `f` of its own, the family form that
`FunctionDecision` describes.

A row whose parameters give several sets of values, separated by `;`, pairs each set with intervals: those that the
set names after `on`, as in `on [0, 5]: a = 0.2, 1, n = 4(2)12`, or the row's only interval.
"""

import itertools
import re
from dataclasses import dataclass, replace

import mpmath
import sympy as sp

from .data_files import SourceRow
from .formula_expressions import FormulaExpression, TranslationError
from .formulas import SurveyFormula
from .helpers import ASSIGNMENT, MAX_INSTANCES, parse_parameters
from .intervals import Interval, ParsedIntervals

# ON_INTERVALS matches the start of a set of values that names its intervals, as in `on [0, 5]: `.
ON_INTERVALS = re.compile(r"\s*on\s+(.+?):\s+")
# CHECK_FRACTIONS are the positions in an interval, as fractions of its width, at which a row's own function is
# compared with the formula's function.
CHECK_FRACTIONS = (0.13, 0.29, 0.41, 0.58, 0.77, 0.94)


class PublishedTestFunctionsError(Exception):
    """A `PublishedTestFunctionsError` reports a formula whose published test functions this module cannot read."""


# ==================================================================================================
#  PublishedTestFunction
# ==================================================================================================
@dataclass(frozen=True)
class PublishedTestFunction:
    """A `PublishedTestFunction` holds 1 published test function: a row, its parameter values and 1 interval.

    `parameter_values` holds an exact sympy value for each parameter of the formula, keyed by its survey name.
    """

    row: SourceRow
    parameter_values: tuple[tuple[str, sp.Expr], ...]
    interval: Interval


# ==================================================================================================
#  PublishedFormula
# ==================================================================================================
@dataclass(frozen=True)
class PublishedFormula:
    """A `PublishedFormula` holds a formula's function, its variable, its parameters and its published test functions.

    Attributes:
        f: The formula's function, as the survey writes it.
        variable: The name of the function's variable.
        survey_parameter_names: The survey names of the function's parameters, in the order in which the first row's
            parameters name them.
        test_functions: The published test functions, row by row, in the order of each row's values and intervals.
        is_family_form: Whether `f` is a family form from `formulas.csv` (`FunctionDecision` describes it), and not the
            first row's `f`.
    """

    f: str
    variable: str
    survey_parameter_names: tuple[str, ...]
    test_functions: tuple[PublishedTestFunction, ...]
    is_family_form: bool

    @property
    def has_interval_parameters(self) -> bool:
        """Return whether the test functions lie on more than 1 interval, so that each tuple carries its `a` and `b`."""
        return len({test_function.interval.key for test_function in self.test_functions}) > 1

    def check_rows(self) -> None:
        """Check that each row's own `f` gives the formula's function, for each of the row's test functions.

        The 2 functions are compared by value at `CHECK_FRACTIONS` of each interval, in 30-digit arithmetic. The
        formula's function is 1 of 2 kinds:

        - where `is_family_form` holds, it is the family form that a person wrote to cover all the rows' functions, and
          it must equal each row's function exactly;
        - otherwise, it is the first row's `f`, and another row's `f` may equal it times a constant; that constant is -1
          for a row that writes the equation with its 2 sides swapped.

        Raises:
            PublishedTestFunctionsError: If the formula's function cannot be translated, or a row's function differs
                from the formula's.
        """
        # the check reads only the sympy expression, so any Python names will do; adding `_` to each name keeps it from
        # being a Python keyword, such as `lambda`
        try:
            formula_expression = FormulaExpression.from_text(
                self.f, self.variable, {name: f"{name}_" for name in self.survey_parameter_names}
            )
        except TranslationError as error:
            raise PublishedTestFunctionsError(str(error)) from error
        for row in dict.fromkeys(test_function.row for test_function in self.test_functions):
            row_python_names = {name: name for name in FormulaExpression.free_names(row.f) if name != self.variable}
            try:
                row_expression = FormulaExpression.from_text(row.f, self.variable, row_python_names)
            except TranslationError as error:
                raise PublishedTestFunctionsError(f"{row.row_id}: {error}") from error
            for test_function in (test_function for test_function in self.test_functions if test_function.row == row):
                row_values = {name: values[0] for name, values in parse_parameters(row.parameters).items()}
                formula_function = formula_expression.mpmath_function(dict(test_function.parameter_values))
                row_function = row_expression.mpmath_function({**row_values, **dict(test_function.parameter_values)})
                ratios = self._value_ratios(formula_function, row_function, test_function.interval)
                if not ratios or (self.is_family_form and any(abs(r - 1) > 1e-20 for r in ratios)):
                    raise PublishedTestFunctionsError(f"{row.row_id}: the row's f differs from the formula's function")
                elif any(abs(r - ratios[0]) > 1e-20 * abs(ratios[0]) for r in ratios):
                    raise PublishedTestFunctionsError(
                        f"{row.row_id}: the row's f is not a multiple of the formula's function"
                    )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _value_ratios(formula_function: object, row_function: object, interval: Interval) -> list:
        """Return the ratios of the 2 functions' values at `CHECK_FRACTIONS` of the interval, where both are nonzero."""
        lower, upper = sp.sympify(interval.lower), sp.sympify(interval.upper)
        ratios = []
        with mpmath.workdps(30):
            for fraction in CHECK_FRACTIONS:
                x = mpmath.mpf(sp.N(lower + fraction * (upper - lower), 40))
                try:
                    formula_value, row_value = formula_function(x), row_function(x)
                except (ArithmeticError, ValueError, TypeError):
                    continue
                if formula_value != 0 and row_value != 0:
                    ratios.append(row_value / formula_value)
        return ratios

    @staticmethod
    def _find_variable(names: list[str], assigned_names: set[str], notes: str) -> str:
        """Return the function's variable: `x`, the name that the notes call the unknown, or the only other name.

        Raises:
            PublishedTestFunctionsError: If none of these gives 1 name.
        """
        named = re.search(r"unknown `([A-Za-z_][A-Za-z0-9_]*)`", notes, flags=re.IGNORECASE)
        free = [name for name in names if name not in assigned_names and name != "e"]
        if "x" in names:
            return "x"
        elif named and named.group(1) in names:
            return named.group(1)
        elif len(free) == 1:
            return free[0]
        else:
            raise PublishedTestFunctionsError(f"the variable of {names} is unclear")

    @staticmethod
    def _value_sets(row: SourceRow, values_text: str) -> list[tuple[dict[str, list], tuple[Interval, ...]]]:
        """Return the row's sets of parameter values, each with its published intervals.

        `values_text` is the row's own parameters, followed by its values from `formulas.csv`, if any. A set that
        does not assign a parameter takes the first set's values of it.

        Raises:
            PublishedTestFunctionsError: If the row gives several sets of values and more than 1 interval, and a set
                does not name its intervals.
        """
        row_intervals = ParsedIntervals.from_source_row(row).intervals
        groups = [group for group in values_text.replace("`", "").split(";") if group.strip()]
        names_per_group = [{match.group(1) for match in ASSIGNMENT.finditer(group)} for group in groups]
        is_reassigned = any(
            sum(name in names for names in names_per_group) > 1 for name in set().union(*names_per_group)
        )
        if not is_reassigned:
            return [(parse_parameters(values_text), row_intervals)]
        else:
            value_sets = []
            for group in groups:
                on_match = ON_INTERVALS.match(group)
                if on_match:
                    intervals = ParsedIntervals.from_source_row(replace(row, interval=on_match.group(1))).intervals
                    assignments = group[on_match.end() :]
                elif len(row_intervals) == 1:
                    intervals, assignments = row_intervals, group
                else:
                    raise PublishedTestFunctionsError(
                        f"{row.row_id}: a set of parameter values does not name its intervals"
                    )
                first_set = value_sets[0][0] if value_sets else {}
                value_sets.append(({**first_set, **parse_parameters(assignments)}, intervals))
            return value_sets

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_survey(cls, survey_formula: SurveyFormula) -> "PublishedFormula":
        """Return the formula of a line of `formulas.csv`, with the test functions of its rows.

        Raises:
            PublishedTestFunctionsError: If the line's `parameters` does not give 1 set per row, the variable is
                unclear, a parameter has no published value, there are more than `MAX_INSTANCES` test functions, no
                test function has an interval, or a row's function differs from the formula's.
        """
        formulas_table_line = survey_formula.formulas_table_line
        rows = survey_formula.rows
        f = formulas_table_line.function_decision.f or rows[0].f
        values_per_row = formulas_table_line.values_per_row()
        if len(values_per_row) != len(rows):
            raise PublishedTestFunctionsError(
                f"{formulas_table_line.formula_id}: its parameters do not give 1 set per row"
            )
        values_texts = [
            f"{row.parameters}; {values}" if values.strip() else row.parameters
            for row, values in zip(rows, values_per_row, strict=True)
        ]
        assigned_names = {
            match.group(1) for text in values_texts for match in ASSIGNMENT.finditer(text.replace("`", ""))
        }
        names = FormulaExpression.free_names(f)
        variable = cls._find_variable(names, assigned_names, rows[0].notes)
        survey_parameter_names = [
            name for name in names if name != variable and (name != "e" or name in assigned_names)
        ]
        # the first row's parameters give the order of the formula's parameters
        first_row_order = list(parse_parameters(values_texts[0]))
        survey_parameter_names.sort(
            key=lambda name: first_row_order.index(name) if name in first_row_order else len(names)
        )
        test_functions = []
        for row, values_text in zip(rows, values_texts, strict=True):
            for values, intervals in cls._value_sets(row, values_text):
                missing = [name for name in survey_parameter_names if not values.get(name)]
                if missing:
                    raise PublishedTestFunctionsError(
                        f"{row.row_id}: the parameter {missing[0]} has no published value"
                    )
                for combo in itertools.product(*(values[name] for name in survey_parameter_names)):
                    parameter_values = tuple(zip(survey_parameter_names, combo, strict=True))
                    test_functions += [
                        PublishedTestFunction(row, parameter_values, interval)
                        for interval in intervals
                        if interval.matches_parameter_values(parameter_values)
                    ]
        if len(test_functions) > MAX_INSTANCES:
            raise PublishedTestFunctionsError(
                f"{formulas_table_line.formula_id}: more than {MAX_INSTANCES} test functions"
            )
        elif not test_functions:
            raise PublishedTestFunctionsError(
                f"{formulas_table_line.formula_id}: no test function has a usable interval"
            )
        else:
            published_formula = cls(
                f=f,
                variable=variable,
                survey_parameter_names=tuple(survey_parameter_names),
                test_functions=tuple(test_functions),
                is_family_form=bool(formulas_table_line.function_decision.f),
            )
            if len(rows) > 1:
                published_formula.check_rows()
            return published_formula
