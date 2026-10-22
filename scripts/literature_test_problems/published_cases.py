"""This module reads the published test functions of 1 formula from the survey: its function and its cases.

A case is 1 test function that a source publishes: 1 combination of the formula's parameter values, on 1 interval. A
formula's function is the `f` of its first row, or the `f` of its line in `formulas.csv`, which a person gives in
`formula_decisions.csv` for a formula whose rows give 1 function with other values of a parameter; the line's
`parameters` then gives each row's values of those parameters.

A row whose parameters give several sets of values, separated by `;`, pairs each set with intervals: those that the
set names after `on`, as in `on [0, 5]: a = 0.2, 1, n = 4(2)12`, or the row's only interval.
"""

import itertools
import re
from dataclasses import dataclass, replace

import mpmath
import sympy as sp

from .data_files import Source, SourceRow
from .formula_expressions import FormulaExpression, TranslationError
from .formulas import FormulasTableLine
from .helpers import ASSIGNMENT, MAX_INSTANCES, parse_parameters
from .intervals import Interval, ParsedIntervals

# ON_INTERVALS matches the start of a set of values that names its intervals, as in `on [0, 5]: `.
ON_INTERVALS = re.compile(r"\s*on\s+(.+?):\s+")
# CHECK_FRACTIONS are the positions in an interval, as fractions of its width, at which a row's own function is
# compared with the formula's function.
CHECK_FRACTIONS = (0.13, 0.29, 0.41, 0.58, 0.77, 0.94)


class PublicationError(Exception):
    """A `PublicationError` reports a formula whose cases the survey does not give in a form that this module reads."""


# ==================================================================================================
#  PublishedCase
# ==================================================================================================
@dataclass(frozen=True)
class PublishedCase:
    """A `PublishedCase` holds 1 published test function: a row, its values of the formula's parameters and 1 interval.

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
    """A `PublishedFormula` holds a formula's function, its variable, its parameters and its published cases.

    Attributes:
        f: The formula's function, as the survey writes it.
        variable: The name of the function's variable.
        parameter_names: The survey names of the function's parameters, in the order in which the first row's
            parameters name them.
        cases: The published cases, row by row, in the order of each row's values and intervals.
    """

    f: str
    variable: str
    parameter_names: tuple[str, ...]
    cases: tuple[PublishedCase, ...]

    @property
    def rows(self) -> tuple[SourceRow, ...]:
        """Return the formula's rows that have cases, in the order of the formula's rows."""
        return tuple(dict.fromkeys(case.row for case in self.cases))

    def check_rows(self, expression: FormulaExpression, is_template: bool) -> None:
        """Check that each row's own `f` gives the formula's function at each of the row's cases.

        The 2 functions are compared by value at `CHECK_FRACTIONS` of each interval, in 30-digit arithmetic. With
        `is_template`, the formula's function is a person's family form of the rows' functions, which must give each
        row's function exactly; otherwise it is the first row's `f`, and the other rows may give it multiplied by a
        constant, the sign flip of an equation's other difference form included.

        Raises:
            PublicationError: If a row's function differs from the formula's.
        """
        for row in self.rows:
            row_names = {name: name for name in FormulaExpression.free_names(row.f) if name != self.variable}
            try:
                row_expression = FormulaExpression.from_text(row.f, self.variable, row_names)
            except TranslationError as error:
                raise PublicationError(f"{row.row_id}: {error}") from error
            for case in (case for case in self.cases if case.row == row):
                values = {sp.Symbol(name): value for name, value in case.parameter_values}
                row_values = {sp.Symbol(name): value for name, value in parse_parameters(row.parameters).items()}
                formula_function = sp.lambdify(
                    expression.variable, expression.sympy_expr.subs(values), modules="mpmath"
                )
                row_function = sp.lambdify(
                    row_expression.variable,
                    row_expression.sympy_expr.subs({**{s: v[0] for s, v in row_values.items()}, **values}),
                    modules="mpmath",
                )
                ratios = self._value_ratios(formula_function, row_function, case.interval)
                if not ratios or (is_template and any(abs(r - 1) > 1e-20 for r in ratios)):
                    raise PublicationError(f"{row.row_id}: the row's f differs from the formula's function")
                elif any(abs(r - ratios[0]) > 1e-20 * abs(ratios[0]) for r in ratios):
                    raise PublicationError(f"{row.row_id}: the row's f is not a multiple of the formula's function")

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
    def _find_variable(names: list[str], parameter_names: set[str], notes: str) -> str:
        """Return the function's variable: `x`, the name that the notes call the unknown, or the only other name.

        Raises:
            PublicationError: If none of these gives 1 name.
        """
        named = re.search(r"unknown `([A-Za-z_][A-Za-z0-9_]*)`", notes, flags=re.IGNORECASE)
        free = [name for name in names if name not in parameter_names and name != "e"]
        if "x" in names:
            return "x"
        elif named and named.group(1) in names:
            return named.group(1)
        elif len(free) == 1:
            return free[0]
        else:
            raise PublicationError(f"the variable of {names} is unclear")

    @staticmethod
    def _value_sets(row: SourceRow, values_text: str) -> list[tuple[dict[str, list], tuple[Interval, ...]]]:
        """Return the row's sets of parameter values, each with the intervals that it is published on.

        `values_text` is the row's own parameters, followed by its values from `formulas.csv`, if any. A set that
        does not assign a parameter takes the first set's values of it.

        Raises:
            PublicationError: If several sets are published but some set does not name its intervals, while the row
                has more than 1.
        """
        row_intervals = ParsedIntervals.from_source_row(row).intervals
        groups = [group for group in values_text.replace("`", "").split(";") if group.strip()]
        names_per_group = [{match.group(1) for match in ASSIGNMENT.finditer(group)} for group in groups]
        is_reassigned = any(
            sum(name in names for names in names_per_group) > 1 for name in set().union(*names_per_group)
        )
        if not is_reassigned:
            return [(parse_parameters(values_text), row_intervals)]
        value_sets = []
        for group in groups:
            on_match = ON_INTERVALS.match(group)
            if on_match:
                intervals = ParsedIntervals.from_source_row(replace(row, interval=on_match.group(1))).intervals
                assignments = group[on_match.end() :]
            elif len(row_intervals) == 1:
                intervals, assignments = row_intervals, group
            else:
                raise PublicationError(f"{row.row_id}: a set of parameter values does not name its intervals")
            first_set = value_sets[0][0] if value_sets else {}
            value_sets.append(({**first_set, **parse_parameters(assignments)}, intervals))
        return value_sets

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_survey(cls, formulas_table_line: FormulasTableLine, source: Source) -> "PublishedFormula":
        """Return the formula of a line of `formulas.csv`, with the cases of its rows.

        Raises:
            PublicationError: If the line's `parameters` does not give 1 set per row, the variable is unclear, a
                parameter has no published value, the cases are more than `MAX_INSTANCES`, or no case has an
                interval.
        """
        rows = [source.find_row(row_id) for row_id in formulas_table_line.row_ids]
        f = formulas_table_line.function.f or rows[0].f
        row_values = formulas_table_line.function.row_parameters() or [""] * len(rows)
        if len(row_values) != len(rows):
            raise PublicationError(f"{formulas_table_line.formula_id}: its parameters do not give 1 set per row")
        values_texts = [
            f"{row.parameters}; {values}" if values.strip() else row.parameters
            for row, values in zip(rows, row_values, strict=True)
        ]
        assigned_names = {
            match.group(1) for text in values_texts for match in ASSIGNMENT.finditer(text.replace("`", ""))
        }
        names = FormulaExpression.free_names(f)
        variable = cls._find_variable(names, assigned_names, rows[0].notes)
        parameter_names = [name for name in names if name != variable and (name != "e" or name in assigned_names)]
        # the first row's parameters give the order of the formula's parameters
        first_row_order = list(parse_parameters(values_texts[0]))
        parameter_names.sort(key=lambda name: first_row_order.index(name) if name in first_row_order else len(names))
        cases = []
        for row, values_text in zip(rows, values_texts, strict=True):
            for values, intervals in cls._value_sets(row, values_text):
                missing = [name for name in parameter_names if not values.get(name)]
                if missing:
                    raise PublicationError(f"{row.row_id}: the parameter {missing[0]} has no published value")
                for combo in itertools.product(*(values[name] for name in parameter_names)):
                    parameter_values = tuple(zip(parameter_names, combo, strict=True))
                    cases += [
                        PublishedCase(row, parameter_values, interval)
                        for interval in intervals
                        if interval.matches_parameter_values(parameter_values)
                    ]
        if len(cases) > MAX_INSTANCES:
            raise PublicationError(f"{formulas_table_line.formula_id}: more than {MAX_INSTANCES} cases")
        elif not cases:
            raise PublicationError(f"{formulas_table_line.formula_id}: no case has a usable interval")
        return cls(f=f, variable=variable, parameter_names=tuple(parameter_names), cases=tuple(cases))
