"""This module parses a row's f and parameters into the sympy forms that the matching compares."""

import itertools
import re
import signal
from dataclasses import dataclass

import mpmath
import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, parse_expr, rationalize, standard_transformations

from .data_files import SourceRow

# fmt: off
FUNCTIONS = {
    "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
    "log": sp.log, "ln": sp.log, "log10": lambda a: sp.log(a, 10), "log2": lambda a: sp.log(a, 2),
    "sqrt": sp.sqrt, "cbrt": sp.cbrt, "abs": sp.Abs, "sign": sp.sign, "floor": sp.floor, "ceil": sp.ceiling,
    "erf": sp.erf, "erfc": sp.erfc, "Gamma": sp.gamma, "gamma": sp.gamma,
    "J0": lambda a: sp.besselj(0, a), "Y0": lambda a: sp.bessely(0, a), "besselj": sp.besselj,
    "bessely": sp.bessely, "max": sp.Max, "min": sp.Min, "atan2": sp.atan2,
}
CONSTANTS = {"pi": sp.pi, "inf": sp.oo}
# The words in TEXT_WORDS mark an `f` as conditions or prose, which the script does not parse.
TEXT_WORDS = {
    "if", "otherwise", "for", "given", "with", "where", "sum", "sum_", "integral", "det", "fl", "not", "in", "and",
    "or", "arbitrary",
}
# fmt: on
# IDENTIFIER matches a name that is not part of a number or of a longer name.
IDENTIFIER = re.compile(r"(?<![0-9.A-Za-z_])([A-Za-z_][A-Za-z0-9_]*)")
# ASSIGNMENT matches `name =` in the parameters, but not `==`, `<=`, `>=` or `!=`.
ASSIGNMENT = re.compile(r"(?<![A-Za-z0-9_<>!=])([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*")
# NUMBER_PREFIX matches the leading numeric part of a listed value, such as `2*pi` or `1e-3`, before any text.
NUMBER_PREFIX = re.compile(r"^[-+0-9.()*/^ ]*(?:pi)?[-+0-9.()*/^ eE]*")
TRANSFORMATIONS = (*standard_transformations, convert_xor, rationalize)
# The value comparison evaluates each instance at these x-values.
SAMPLE_POINTS = ["-2.7", "-1.3", "-0.6", "-0.15", "0.11", "0.37", "0.73", "1.21", "1.9", "2.6", "3.7", "5.3"]
MAX_INSTANCES = 64
# PARSE_TIMEOUT_SECONDS limits the time that parsing a row and computing its scaled values may take.
PARSE_TIMEOUT_SECONDS = 10
X = sp.Symbol("x")


class ParseError(Exception):
    """A `ParseError` reports a row's f or parameters that the script does not parse."""


class ParseTimeoutError(Exception):
    """A `ParseTimeoutError` reports parsing or evaluating a row that took too long."""


@dataclass(frozen=True)
class ParsedRow:
    """A `ParsedRow` holds a row's instances, 1 per combination of its parameter values, and its family form.

    All forms are canonical (`_normalize`), and the family form keeps the parameters as symbols. `has_values` tells
    whether any parameter of the expression has values; only then do the instances differ from the family form.
    `scaled_values` holds each instance's values at the sample points, divided by the first finite nonzero one; an
    instance gets None where it has free symbols other than x, or fewer than 4 finite values.
    """

    instances: tuple[sp.Expr, ...]
    family: sp.Expr
    has_values: bool
    scaled_values: tuple[tuple | None, ...]

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
    def _parse_expression(text: str, parameters: dict) -> sp.Expr:
        """Parse 1 expression, or an equation `lhs = rhs` into `lhs - rhs`."""
        local = ParsedRow._local_names(text, parameters)
        # `lambda` is a Python keyword, which sympy's parser cannot take as a name
        text = re.sub(r"\blambda\b", "lambda_", text)
        if "lambda" in local:
            local["lambda_"] = local.pop("lambda")
        sides = text.split("=")
        if len(sides) > 2:
            raise ParseError("several equals signs")
        try:
            parsed = [parse_expr(side, local_dict=local, transformations=TRANSFORMATIONS) for side in sides]
        except ParseTimeoutError:
            raise
        except Exception as error:  # sympy's parser raises many kinds of errors
            raise ParseError(f"sympy: {type(error).__name__}") from error
        if len(parsed) == 2:
            return parsed[0] - parsed[1]
        else:
            return parsed[0]

    @staticmethod
    def _local_names(text: str, parameters: dict) -> dict:
        """Return what each name in an expression means to sympy's parser: a function, a constant or a symbol.

        `e` is Euler's number unless a parameter is named `e`.
        """
        local = {}
        for match in IDENTIFIER.finditer(text):
            name = match.group(1)
            is_call = text[match.end() :].lstrip().startswith("(")
            if is_call and name not in FUNCTIONS:
                raise ParseError(f"unknown function {name}")
            elif is_call:
                local[name] = FUNCTIONS[name]
            elif name in CONSTANTS:
                local[name] = CONSTANTS[name]
            elif name == "e" and "e" not in parameters:
                local[name] = sp.E
            else:
                local[name] = sp.Symbol(name)
        return local

    @staticmethod
    def _parse_parameters(text: str) -> dict[str, list]:
        """Return the numeric values of each parameter that the text assigns, as {name: [values]}."""
        text = text.replace("`", "")
        matches = list(ASSIGNMENT.finditer(text))
        values: dict[str, list] = {}
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            # a value list ends at `;` or at a remark in parentheses
            chunk = re.split(r";|\s\(", text[match.end() : end])[0]
            for value in ParsedRow._parse_value_list(chunk):
                if value not in values.setdefault(match.group(1), []):
                    values[match.group(1)].append(value)
        return {name: vals for name, vals in values.items() if vals}

    @staticmethod
    def _parse_value_list(chunk: str) -> list:
        """Return the numbers that 1 assignment lists.

        The list expands `1, 2, ..., 8` and the step notation `1(1)19`, 1 to 19 in steps of 1.
        """
        step_range = re.match(r"\s*(-?\d+)\((\d+)\)(-?\d+)", chunk)
        if step_range:
            start, step, stop = (int(g) for g in step_range.groups())
            return [sp.Integer(v) for v in range(start, stop + 1, step)]
        pieces = [p.strip() for p in chunk.split(",")]
        if "..." in pieces:
            return ParsedRow._expand_ellipsis(pieces)
        values = []
        for piece in pieces:
            prefix = NUMBER_PREFIX.match(piece).group(0).strip()
            if not prefix:
                continue
            try:
                value = parse_expr(
                    prefix, transformations=TRANSFORMATIONS, local_dict={"pi": sp.pi, "e": sp.E, "E": sp.E}
                )
            except Exception:  # noqa: BLE001 - a piece that does not parse is not a value
                continue
            if value.is_Float:
                values.append(sp.nsimplify(value, rational=True))
            elif value.is_number:
                values.append(value)
        return values

    @staticmethod
    def _expand_ellipsis(pieces: list[str]) -> list:
        """Return the integers of `first, second, ..., last`.

        The result is [] if `...` is not second to last, if the step is not positive, or if the range spans more than
        40 steps.
        """
        ints = [p for p in pieces if re.fullmatch(r"-?\d+", p)]
        if len(ints) >= 2 and pieces.index("...") == len(pieces) - 2:
            first, last = int(ints[0]), int(ints[-1])
            step = int(ints[1]) - first if len(ints) >= 3 else 1
            if step > 0 and (last - first) // step <= 40:
                return [sp.Integer(v) for v in range(first, last + 1, step)]
            else:
                return []
        else:
            return []

    @staticmethod
    def _find_variable(expr: sp.Expr, parameters: dict, notes: str) -> sp.Symbol:
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

    @staticmethod
    def _on_alarm(signum: int, frame: object) -> None:
        """Stop parsing a row that takes too long."""
        raise ParseTimeoutError

    @classmethod
    def _parse(cls, row: SourceRow) -> "ParsedRow":
        """Parse a row into its instances, family form and scaled values, or raise `ParseError` with the reason."""
        if not row.f:
            raise ParseError("not 1 expression")
        words = set(IDENTIFIER.findall(row.f))
        if words & TEXT_WORDS or "..." in row.f or "<" in row.f or ">" in row.f or "!=" in row.f:
            raise ParseError("conditions or prose")
        parameters = cls._parse_parameters(row.parameters)
        expr = cls._parse_expression(row.f, parameters)
        expr = expr.subs(cls._find_variable(expr, parameters, row.notes), X)
        assigned = sorted((s for s in expr.free_symbols if s.name in parameters and s != X), key=lambda s: s.name)
        combos = list(itertools.islice(itertools.product(*(parameters[s.name] for s in assigned)), MAX_INSTANCES + 1))
        if len(combos) > MAX_INSTANCES:
            raise ParseError("too many parameter combinations")
        instances = tuple(cls._normalize(expr.subs(dict(zip(assigned, combo, strict=True)))) for combo in combos)
        return cls(
            instances=instances,
            family=cls._normalize(expr),
            has_values=bool(assigned),
            scaled_values=tuple(cls._scaled_values(instance) for instance in instances),
        )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_source_row(cls, row: SourceRow) -> "ParsedRow":
        """Parse a row, or raise `ParseError` with the reason, or `ParseTimeoutError` after `PARSE_TIMEOUT_SECONDS`.

        Python installs a SIGALRM handler only on Unix and in the main thread, so parsing works only there.
        """
        signal.signal(signal.SIGALRM, cls._on_alarm)
        signal.alarm(PARSE_TIMEOUT_SECONDS)
        try:
            return cls._parse(row)
        finally:
            signal.alarm(0)
