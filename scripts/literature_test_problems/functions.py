"""This module parses a row's f and parameters into the sympy forms of its function that the matching compares."""

import itertools
import re
from dataclasses import dataclass

import mpmath
import sympy as sp

from .data_files import SourceRow
from .helpers import ASSIGNMENT, IDENTIFIER, MAX_INSTANCES, ParseError, TimeLimitContext, parse_math, parse_parameters

# fmt: off
# The words in TEXT_WORDS mark an `f` as conditions or prose, which the script does not parse.
TEXT_WORDS = {
    "if", "otherwise", "for", "given", "with", "where", "sum", "sum_", "integral", "det", "fl", "not", "in", "and",
    "or", "arbitrary",
}
# fmt: on
# The value comparison evaluates each instance at these x-values.
SAMPLE_POINTS = ["-2.7", "-1.3", "-0.6", "-0.15", "0.11", "0.37", "0.73", "1.21", "1.9", "2.6", "3.7", "5.3"]
X = sp.Symbol("x")


# ==================================================================================================
#  ParsedFunction
# ==================================================================================================
@dataclass(frozen=True)
class ParsedFunction:
    """A `ParsedFunction` holds a row's instances, 1 per combination of its parameter values, and its family form.

    All forms are canonical (`_normalize`), and the family form keeps the parameters as symbols. Its other fields are
    these:

    - `instance_parameter_values` holds, for each instance, the value of each parameter of the expression, as
      `(name, value)` pairs.
    - `has_value_sets` tells whether the parameters give several sets of values, separated by `;`, for 2 or more
      parameters, as in `a = -40, b = -1; a = -100, b = -2`: the instances combine every value of each parameter, so
      some may be combinations that the source never gives.
    - `scaled_values` holds each instance's values at the sample points, divided by the first finite nonzero one; an
      instance gets None where it has free symbols other than x, or fewer than 4 finite values.
    """

    instances: tuple[sp.Expr, ...]
    instance_parameter_values: tuple[tuple[tuple[str, sp.Expr], ...], ...]
    family: sp.Expr
    has_value_sets: bool
    scaled_values: tuple[tuple | None, ...]

    # --------------------------------------------------------------------------
    #  Parsing
    # --------------------------------------------------------------------------
    @staticmethod
    def parse_expression(text: str, parameters: dict) -> sp.Expr:
        """Parse 1 expression, or an equation `lhs = rhs` into `lhs - rhs`."""
        sides = text.split("=")
        if len(sides) > 2:
            raise ParseError("several equals signs")
        parsed = [parse_math(side, parameters) for side in sides]
        if len(parsed) == 2:
            return parsed[0] - parsed[1]
        else:
            return parsed[0]

    @staticmethod
    def find_variable(expr: sp.Expr, parameters: dict, notes: str) -> sp.Symbol:
        """Return the unknown: `x`, the symbol that the notes name, or the only symbol that is not a parameter."""
        names = {s.name: s for s in expr.free_symbols}
        if "x" in names:
            return names["x"]
        named = re.search(r"unknown `([A-Za-z_][A-Za-z0-9_]*)`", notes, flags=re.IGNORECASE)
        if named and named.group(1) in names:
            return names[named.group(1)]
        free = [s for name, s in names.items() if name not in parameters]
        if len(free) == 1:
            return free[0]
        else:
            raise ParseError("unknown variable unclear")

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _scaled_values(expr: sp.Expr) -> tuple | None:
        """Return 1 instance's scaled values, in 40-digit arithmetic, or None if it has too few values."""
        if expr.free_symbols - {X}:
            return None
        function = sp.lambdify(X, expr, modules="mpmath")
        values = []
        with mpmath.workdps(40):
            for point in SAMPLE_POINTS:
                try:
                    value = mpmath.mpc(function(mpmath.mpf(point)))
                    values.append(value if mpmath.isfinite(value) else None)
                except Exception:  # noqa: BLE001 - any failure to evaluate leaves out that sample point
                    values.append(None)
            reference = next((v for v in values if v is not None and abs(v) > mpmath.mpf(10) ** -30), None)
            if reference is None or sum(v is not None for v in values) < 4:
                return None
            else:
                return tuple(
                    None
                    if v is None
                    else (mpmath.nstr((v / reference).real, 10), mpmath.nstr((v / reference).imag, 10))
                    for v in values
                )

    @staticmethod
    def _has_value_sets(text: str, varied_names: set[str]) -> bool:
        """Return whether the parameters give several sets of values for 2 or more parameters.

        That holds when 2 or more parameters have several values and 1 of them is assigned in several groups separated
        by `;`.
        """
        groups = [
            {match.group(1) for match in ASSIGNMENT.finditer(group)} for group in text.replace("`", "").split(";")
        ]
        is_reassigned = False
        if len(varied_names) >= 2:
            for name in varied_names:
                if sum(name in group for group in groups) >= 2:
                    is_reassigned = True
        return is_reassigned

    @staticmethod
    def _normalize(expr: sp.Expr) -> sp.Expr:
        """Return a canonical form: floats as exact rationals, no constant factor, a fixed sign, symbols renamed.

        The free symbols other than x are renamed q0, q1, ..., so that 2 sources that name a parameter differently
        still match: with up to 3 symbols, every order is tried and the form whose `srepr` sorts first is kept; with
        more, the order of their names is used.
        """
        expr = expr.xreplace({f: sp.Rational(str(f)) for f in expr.atoms(sp.Float)})
        others = sorted((s for s in expr.free_symbols if s != X), key=lambda s: s.name)
        if len(others) <= 3:
            orders = itertools.permutations(range(len(others)))
        else:
            orders = [range(len(others))]
        forms = []
        for order in orders:
            form = expr.xreplace({s: sp.Symbol(f"q{k}") for s, k in zip(others, order, strict=True)})
            _, form = form.as_content_primitive()
            forms.append(-form if form.could_extract_minus_sign() else form)
        return min(forms, key=sp.srepr)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_source_row(cls, row: SourceRow) -> "ParsedFunction":
        """Parse a row, or raise `ParseError` with the reason, or `ParseTimeoutError` after `PARSE_TIMEOUT_SECONDS`.

        Parsing works only on Unix and in the main thread, where Python can install the SIGALRM handler of
        `TimeLimitContext`.
        """
        with TimeLimitContext():
            if not row.f:
                raise ParseError("not 1 expression")
            words = set(IDENTIFIER.findall(row.f))
            if words & TEXT_WORDS or "..." in row.f or "<" in row.f or ">" in row.f or "!=" in row.f:
                raise ParseError("conditions or prose")
            parameters = parse_parameters(row.parameters)
            expr = cls.parse_expression(row.f, parameters)
            expr = expr.subs(cls.find_variable(expr, parameters, row.notes), X)
            assigned = sorted((s for s in expr.free_symbols if s.name in parameters and s != X), key=lambda s: s.name)
            combos = list(
                itertools.islice(itertools.product(*(parameters[s.name] for s in assigned)), MAX_INSTANCES + 1)
            )
            if len(combos) > MAX_INSTANCES:
                raise ParseError("too many parameter combinations")
            instances = tuple(cls._normalize(expr.subs(dict(zip(assigned, combo, strict=True)))) for combo in combos)
            return cls(
                instances=instances,
                instance_parameter_values=tuple(
                    tuple((s.name, value) for s, value in zip(assigned, combo, strict=True)) for combo in combos
                ),
                family=cls._normalize(expr),
                has_value_sets=cls._has_value_sets(
                    row.parameters, {s.name for s in assigned if len(parameters[s.name]) > 1}
                ),
                scaled_values=tuple(cls._scaled_values(instance) for instance in instances),
            )
