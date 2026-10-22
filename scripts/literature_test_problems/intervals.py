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
from .helpers import MAX_INSTANCES, ParseError, TimeLimitContext, parse_math, parse_parameters, parse_value_list

# NO_INTERVAL matches the start of an interval text that says that the source gives no interval.
NO_INTERVAL = re.compile(r"(none|not given|not printed|not stated)\b", flags=re.IGNORECASE)
# NAME_CHARACTER matches a character after which a bracket opens a function call, such as `U(1, 5)`, not an interval.
NAME_CHARACTER = re.compile(r"[A-Za-z0-9_]")
# SPAN_ASSIGNMENT matches a backtick span that is a whole assignment `name = right side`, such as `n = 1, ..., 10`.
SPAN_ASSIGNMENT = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*(.+?)\s*")


# ==================================================================================================
#  Interval
# ==================================================================================================
@dataclass(frozen=True)
class Interval:
    """An `Interval` holds 1 interval and the values of the parameters that its bounds use.

    `lower` and `upper` are the bounds, each the string of an exact sympy number, the smaller one first, such as
    `pi/2` and `1/10000`: a decimal bound is read as an exact fraction, so `1E-4`, `10^(-4)` and `0.0001` give the
    same text, and 2 intervals are the same interval when their bounds are equal.
    """

    lower: str
    upper: str
    parameter_values: tuple[tuple[str, sp.Expr], ...]

    @property
    def key(self) -> tuple[str, str]:
        """Return the 2 bounds, which identify the interval."""
        return (self.lower, self.upper)

    def matches_parameter_values(self, parameter_values: tuple[tuple[str, sp.Expr], ...]) -> bool:
        """Return whether the interval belongs to an instance with these parameter values.

        The interval belongs to the instance when the interval and the instance give the same value to every parameter
        that they both name, which holds for an interval whose bounds use no parameter of the function.
        """
        instance_values = dict(parameter_values)
        return all(instance_values.get(name, value) == value for name, value in self.parameter_values)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_bounds(cls, bounds: list[sp.Expr], parameter_values: tuple[tuple[str, sp.Expr], ...]) -> "Interval":
        """Return the interval between 2 exact real bounds, given in either order."""
        lower, upper = sorted(bounds, key=lambda bound: sp.N(bound, 50))
        return cls(str(lower), str(upper), parameter_values)


# ==================================================================================================
#  ParsedIntervals
# ==================================================================================================
@dataclass(frozen=True)
class ParsedIntervals:
    """A `ParsedIntervals` holds a row's usable intervals, or why it has none.

    `incomplete_reason` is 1 of these:

    - "no interval" where the text is empty or says that the source gives none;
    - "no usable interval" where the text gives no interval with finite numeric bounds, such as `theta > 0`, a
      starting point, an interval with an infinite bound, or one with bounds that the row gives no values for;
    - "" otherwise.

    `n_unusable` counts the intervals that the text gives but that are left out as not usable.
    """

    intervals: tuple[Interval, ...]
    incomplete_reason: str
    n_unusable: int

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _find_bound_pairs(code: str) -> list[tuple[str, str]]:
        """Return the 2 values, as written, of each bracket that holds exactly 2 values.

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
            bracket = ParsedIntervals._split_bracket(code, i)
            if bracket is None:
                break
            parts, end = bracket
            if i > 0:
                is_call = bool(NAME_CHARACTER.match(code[i - 1]))
            else:
                is_call = False
            if not is_call and len(parts) == 2:
                pairs.append((parts[0].strip(), parts[1].strip()))
            i = end + 1
        return pairs

    @staticmethod
    def _split_bracket(code: str, start: int) -> tuple[list[str], int] | None:
        """Return the comma-separated parts of the bracket that opens at `code[start]`, and where it closes.

        The result is None if the bracket does not close. Commas inside nested brackets do not separate parts.
        """
        depth, parts, part_start = 0, [], start + 1
        for j in range(start, len(code)):
            if code[j] in "[({":
                depth += 1
            elif code[j] in "])}":
                depth -= 1
                if depth == 0:
                    parts.append(code[part_start:j])
                    return parts, j
            elif code[j] == "," and depth == 1:
                parts.append(code[part_start:j])
                part_start = j + 1
        return None

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
    def _evaluate_bounds(
        bounds: tuple[str, str], definitions: dict[str, sp.Expr], values: dict[str, list], parameters: dict
    ) -> list[Interval] | None:
        """Return the intervals that 2 bounds give, 1 per combination of the values of the names that they use.

        The result is None where the bounds are not usable: a bound uses a name that has no values, or is infinite.

        Args:
            bounds: The 2 bounds as the interval text writes them.
            definitions: The names that the interval text defines by an expression, such as `a_n`.
            values: The values of each name that a bound may use: the row's parameters and the names that the
                interval text assigns values to.
            parameters: The row's parameter values, which `parse_math` uses only to tell whether `e` is a parameter.

        Raises:
            ParseError: If a bound does not parse or is not a real number, if the bounds are equal, or if the names
                give more than `MAX_INSTANCES` combinations.
        """
        exprs = [parse_math(bound, parameters) for bound in bounds]
        # a definition may use another definition, so substitute up to 3 levels deep
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
            intervals.append(Interval.from_bounds(numbers, tuple(zip(names, combo, strict=True))))
        return intervals

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_source_row(cls, row: SourceRow) -> "ParsedIntervals":
        """Parse a row's interval text, or raise `ParseError` with the reason, or `ParseTimeoutError` if it is slow.

        Parsing works only on Unix and in the main thread, where Python can install the SIGALRM handler of
        `TimeLimitContext`.
        """
        with TimeLimitContext():
            text = row.interval.strip()
            if not text or NO_INTERVAL.match(text):
                return cls(intervals=(), incomplete_reason="no interval", n_unusable=0)
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
                    evaluated = cls._evaluate_bounds(bounds, definitions, values, row_values)
                    if evaluated is None:
                        n_unusable += 1
                    else:
                        intervals.update(dict.fromkeys(evaluated))
            if intervals:
                return cls(intervals=tuple(intervals), incomplete_reason="", n_unusable=n_unusable)
            else:
                return cls(intervals=(), incomplete_reason="no usable interval", n_unusable=n_unusable)
