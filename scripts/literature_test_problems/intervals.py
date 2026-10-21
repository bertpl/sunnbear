"""This module parses a row's interval text into the intervals that the matching compares.

The text gives each interval as `[a, b]` or `(a, b)`; open and closed bounds count as the same interval. Where the
text holds backticks, only the code between them counts, so that a remark such as `(Ex. 5.3, 5.5)` is not read as an
interval. A bound may use the row's parameters, and names that the interval text itself assigns in backticks: a list
of values such as `` `n = 1, ..., 10` ``, or an expression such as `` `a_n = n^2 + 10^(-9)` ``.
"""

import itertools
import re
from dataclasses import dataclass

import sympy as sp

from .data_files import SourceRow
from .parsing import MAX_INSTANCES, ParseError, TimeLimit, parse_math, parse_parameters, parse_value_list

# NO_INTERVAL matches the start of an interval text that says that the source gives no interval.
NO_INTERVAL = re.compile(r"(none|not given|not printed|not stated)\b", flags=re.IGNORECASE)
# NAME_CHARACTER matches a character after which a bracket opens a function call, such as `U(1, 5)`, not an interval.
NAME_CHARACTER = re.compile(r"[A-Za-z0-9_]")
SPAN_ASSIGNMENT = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*(.+?)\s*")


# ==================================================================================================
#  Interval
# ==================================================================================================
@dataclass(frozen=True)
class Interval:
    """An `Interval` holds 1 interval and the values of the parameters that its bounds use.

    `lower` and `upper` are the bounds as exact sympy numbers in text, the smaller one first, such as `pi/2` and
    `1/10000`: a decimal bound is read as an exact fraction, so `1E-4`, `10^(-4)` and `0.0001` give the same text,
    and 2 intervals are equal when their keys are.
    """

    lower: str
    upper: str
    parameter_values: tuple[tuple[str, sp.Expr], ...]

    @property
    def key(self) -> tuple[str, str]:
        """Return the 2 bounds, which identify the interval."""
        return (self.lower, self.upper)

    def fits(self, parameter_values: tuple[tuple[str, sp.Expr], ...]) -> bool:
        """Return whether the interval belongs to an instance with these parameter values.

        It does when both give the same value to every parameter that both name, which holds for an interval whose
        bounds use no parameter of the function.
        """
        instance_values = dict(parameter_values)
        return all(instance_values.get(name, value) == value for name, value in self.parameter_values)


# ==================================================================================================
#  ParsedIntervals
# ==================================================================================================
@dataclass(frozen=True)
class ParsedIntervals:
    """A `ParsedIntervals` holds a row's usable intervals, or why it has none.

    `incomplete_case` is "no interval" where the text says that the source gives none or is empty, "no usable
    interval" where the text gives no interval with finite numeric bounds, such as `theta > 0`, a starting point, an
    interval with an infinite bound or one with bounds that the row gives no values for, and "" otherwise.
    `n_unusable` counts the intervals that the text gives but that are left out, beside usable ones.
    """

    intervals: tuple[Interval, ...]
    incomplete_case: str
    n_unusable: int

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _find_bound_pairs(code: str) -> list[tuple[str, str]]:
        """Return the 2 bounds of each bracket pair in the code that holds exactly 2 values, as written.

        A bracket opens at `[` or `(` and closes at the matching `]` or `)`, either one, so `[0.1, inf)` counts. A
        bracket right after a name, such as `U(1, 5)`, is a function call, and a bracket with 1 or more than 2
        values, such as `(16)`, is a remark; neither gives an interval.
        """
        pairs = []
        i = 0
        while i < len(code):
            if code[i] not in "[(":
                i += 1
                continue
            depth, parts, start, end = 0, [], i + 1, None
            for j in range(i, len(code)):
                if code[j] in "[({":
                    depth += 1
                elif code[j] in "])}":
                    depth -= 1
                    if depth == 0:
                        end = j
                        break
                elif code[j] == "," and depth == 1:
                    parts.append(code[start:j])
                    start = j + 1
            if end is None:
                break
            parts.append(code[start:end])
            is_call = i > 0 and NAME_CHARACTER.match(code[i - 1])
            if not is_call and len(parts) == 2:
                pairs.append((parts[0].strip(), parts[1].strip()))
            i = end + 1
        return pairs

    @staticmethod
    def _read_assignments(spans: list[str], parameters: dict[str, list]) -> tuple[dict[str, sp.Expr], dict[str, list]]:
        """Return the names that the interval text assigns: those defined by an expression, and those given values.

        Only a span that is a whole assignment `name = ...` counts. An assignment whose right side holds a name, such
        as `a_n = n^2 + 10^(-9)`, defines an expression; any other gives a list of values, such as `n = 1, ..., 10`.
        """
        definitions, values = {}, {}
        for span in spans:
            assignment = SPAN_ASSIGNMENT.fullmatch(span)
            if not assignment:
                continue
            name, right_side = assignment.groups()
            try:
                expr = parse_math(right_side, parameters)
            except ParseError:
                expr = None
            if isinstance(expr, sp.Expr) and expr.free_symbols:
                definitions[name] = expr
            elif parse_value_list(right_side):
                values[name] = parse_value_list(right_side)
        return definitions, values

    @staticmethod
    def _evaluate(
        bounds: tuple[str, str], definitions: dict[str, sp.Expr], values: dict[str, list], parameters: dict
    ) -> list[Interval] | None:
        """Return the intervals that 2 bounds give, 1 per combination of the values of the names that they use.

        The result is None where the bounds are not usable: a bound uses a name that has no values, or is infinite.

        Raises:
            ParseError: If a bound does not parse, is not a real number, or the bounds are equal.
        """
        exprs = [parse_math(bound, parameters) for bound in bounds]
        for _ in range(3):
            exprs = [expr.subs(definitions) for expr in exprs]
        names = sorted({s.name for expr in exprs for s in expr.free_symbols})
        if any(name not in values for name in names):
            return None
        combos = list(itertools.islice(itertools.product(*(values[name] for name in names)), MAX_INSTANCES + 1))
        if len(combos) > MAX_INSTANCES:
            raise ParseError("interval: too many parameter combinations")
        intervals = []
        for combo in combos:
            substitution = {sp.Symbol(name): value for name, value in zip(names, combo, strict=True)}
            numbers = [sp.nsimplify(expr.subs(substitution), rational=True) for expr in exprs]
            if any(number in (sp.oo, -sp.oo) for number in numbers):
                return None
            elif not all(number.is_real and number.is_finite for number in numbers):
                raise ParseError("interval: a bound is not a real number")
            elif sp.simplify(numbers[0] - numbers[1]) == 0:
                raise ParseError("interval: equal bounds")
            lower, upper = sorted(numbers, key=lambda number: sp.N(number, 50))
            intervals.append(Interval(str(lower), str(upper), tuple(zip(names, combo, strict=True))))
        return intervals

    @classmethod
    def _parse(cls, row: SourceRow) -> "ParsedIntervals":
        """Parse a row's interval text, or raise `ParseError` with the reason."""
        text = row.interval.strip()
        if not text or NO_INTERVAL.match(text):
            return cls(intervals=(), incomplete_case="no interval", n_unusable=0)
        if "`" in text:
            spans = re.findall(r"`([^`]*)`", text)
        else:
            spans = [text]
        row_values = parse_parameters(row.parameters)
        definitions, local_values = cls._read_assignments(spans, row_values)
        values = {**row_values, **local_values}
        intervals: dict[Interval, None] = {}
        n_unusable = 0
        for span in spans:
            for bounds in cls._find_bound_pairs(span):
                evaluated = cls._evaluate(bounds, definitions, values, row_values)
                if evaluated is None:
                    n_unusable += 1
                else:
                    intervals.update(dict.fromkeys(evaluated))
        if intervals:
            return cls(intervals=tuple(intervals), incomplete_case="", n_unusable=n_unusable)
        else:
            return cls(intervals=(), incomplete_case="no usable interval", n_unusable=n_unusable)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_source_row(cls, row: SourceRow) -> "ParsedIntervals":
        """Parse a row's interval text, or raise `ParseError` with the reason, or `ParseTimeoutError` if it is slow."""
        with TimeLimit():
            return cls._parse(row)
