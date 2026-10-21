"""This module parses the text of a row's f, parameters and interval into sympy expressions and values."""

import re
import signal

import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, parse_expr, rationalize, standard_transformations

# fmt: off
FUNCTIONS = {
    "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
    "log": sp.log, "ln": sp.log, "log10": lambda a: sp.log(a, 10), "log2": lambda a: sp.log(a, 2),
    "sqrt": sp.sqrt, "cbrt": sp.cbrt, "abs": sp.Abs, "sign": sp.sign, "floor": sp.floor, "ceil": sp.ceiling,
    "ceiling": sp.ceiling,
    "erf": sp.erf, "erfc": sp.erfc, "Gamma": sp.gamma, "gamma": sp.gamma,
    "J0": lambda a: sp.besselj(0, a), "Y0": lambda a: sp.bessely(0, a), "besselj": sp.besselj,
    "bessely": sp.bessely, "max": sp.Max, "min": sp.Min, "atan2": sp.atan2,
}
# fmt: on
CONSTANTS = {"pi": sp.pi, "inf": sp.oo}
# IDENTIFIER matches a name that is not part of a number or of a longer name.
IDENTIFIER = re.compile(r"(?<![0-9.A-Za-z_])([A-Za-z_][A-Za-z0-9_]*)")
# ASSIGNMENT matches `name =` in the parameters, but not `==`, `<=`, `>=` or `!=`.
ASSIGNMENT = re.compile(r"(?<![A-Za-z0-9_<>!=])([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*")
# STEP_RANGE matches the step notation `a(s)b` of a listed value: from a to b in steps of s.
STEP_RANGE = re.compile(r"(-?\d+)\((\d+)\)(-?\d+)")
# NUMBER_PREFIX matches the leading numeric part of a listed value, such as `2*pi` or `1e-3`, before any text.
NUMBER_PREFIX = re.compile(r"^[-+0-9.()*/^ ]*(?:pi)?[-+0-9.()*/^ eE]*")
TRANSFORMATIONS = (*standard_transformations, convert_xor, rationalize)
MAX_INSTANCES = 64
# PARSE_TIMEOUT_SECONDS limits the time that parsing a row and computing its scaled values may take.
PARSE_TIMEOUT_SECONDS = 10


class ParseError(Exception):
    """A `ParseError` reports a row's f, parameters or interval that the script does not parse."""


class ParseTimeoutError(Exception):
    """A `ParseTimeoutError` reports parsing or evaluating a row that took too long."""


# ==================================================================================================
#  TimeLimitContext
# ==================================================================================================
class TimeLimitContext:
    """A `TimeLimitContext` raises `ParseTimeoutError` in the code that it wraps after `PARSE_TIMEOUT_SECONDS`.

    Python installs a SIGALRM handler only on Unix and in the main thread, so parsing works only there.
    """

    def __enter__(self) -> None:
        """Start the alarm."""
        signal.signal(signal.SIGALRM, self._on_alarm)
        signal.alarm(PARSE_TIMEOUT_SECONDS)

    def __exit__(self, *exc_info: object) -> None:
        """Stop the alarm."""
        signal.alarm(0)

    @staticmethod
    def _on_alarm(signum: int, frame: object) -> None:
        """Stop parsing a row that takes too long."""
        raise ParseTimeoutError


# ==================================================================================================
#  Parsing text
# ==================================================================================================
def parse_math(text: str, parameters: dict) -> sp.Expr:
    """Parse 1 expression without an equals sign, or raise `ParseError`.

    `parameters` holds the row's parameter values by name; only their names are used, to tell whether `e` is a
    parameter or Euler's number.
    """
    local = _local_names(text, parameters)
    # `lambda` is a Python keyword, which sympy's parser cannot take as a name
    text = re.sub(r"\blambda\b", "lambda_", text)
    if "lambda" in local:
        local["lambda_"] = local.pop("lambda")
    try:
        return parse_expr(text, local_dict=local, transformations=TRANSFORMATIONS)
    except ParseTimeoutError:
        raise
    except Exception as error:  # sympy's parser raises many kinds of errors
        raise ParseError(f"sympy: {type(error).__name__}") from error


def parse_parameters(text: str) -> dict[str, list]:
    """Return the numeric values of each parameter that the text assigns, as {name: [values]}."""
    text = text.replace("`", "")
    matches = list(ASSIGNMENT.finditer(text))
    values: dict[str, list] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # a value list ends at `;` or at a remark in parentheses
        chunk = re.split(r";|\s\(", text[match.end() : end])[0]
        for value in parse_value_list(chunk):
            if value not in values.setdefault(match.group(1), []):
                values[match.group(1)].append(value)
    return {name: vals for name, vals in values.items() if vals}


def parse_value_list(chunk: str) -> list:
    """Return the numbers that 1 assignment lists, in the order of the list.

    Each comma-separated piece is a number, the step notation `1(1)19` (1 to 19 in steps of 1), or `...` between 2
    numbers, as in `1, 2, ..., 8` or `20, 21, ..., 40, 100, 200, ..., 1000`. The result is [] if an `...` cannot be
    expanded (`_fill_ellipsis`), so that a list is never read in part.
    """
    pieces = [p.strip() for p in chunk.split(",")]
    values = []
    for i, piece in enumerate(pieces):
        step_range = STEP_RANGE.match(piece)
        if piece == "...":
            filled = _fill_ellipsis(pieces, i)
            if filled is None:
                return []
            values.extend(filled)
        elif step_range:
            start, step, stop = (int(g) for g in step_range.groups())
            values.extend(sp.Integer(v) for v in range(start, stop + 1, step))
        else:
            value = _parse_number(piece)
            if value is not None:
                values.append(value)
    return values


def _fill_ellipsis(pieces: list[str], i: int) -> list | None:
    """Return the numbers that the `...` at `pieces[i]` stands for, strictly between its 2 neighbors, or None.

    The step is the difference of the 2 numbers before `...`, or 1 where only 1 number precedes it and both
    neighbors are integers. The result is None if a neighbor is not a plain number, if the step is not positive, if
    the number after `...` is not a whole number of steps away, or if `...` stands for more than 40 steps.
    """
    before_before, before, after = (
        _parse_plain_number(pieces[j]) if 0 <= j < len(pieces) else None for j in (i - 2, i - 1, i + 1)
    )
    if before is None or after is None:
        return None
    elif before_before is not None:
        step = before - before_before
    elif before.is_Integer and after.is_Integer:
        step = sp.Integer(1)
    else:
        return None
    if step > 0:
        n_steps = (after - before) / step
    else:
        n_steps = None
    if n_steps is not None and n_steps.is_Integer and 1 <= n_steps <= 40:
        return [before + k * step for k in range(1, int(n_steps))]
    else:
        return None


def _parse_plain_number(piece: str) -> sp.Rational | None:
    """Return a piece that is a plain decimal number, such as `-24` or `0.1`, as an exact fraction, or None."""
    if re.fullmatch(r"-?\d+(\.\d+)?", piece):
        return sp.Rational(piece)
    else:
        return None


def _parse_number(piece: str) -> sp.Expr | None:
    """Return the number at the start of a listed value, such as `2*pi` in `2*pi rad`, or None if it has none.

    A decimal number is returned as an exact fraction.
    """
    prefix = NUMBER_PREFIX.match(piece).group(0).strip()
    if not prefix:
        return None
    try:
        value = parse_expr(prefix, transformations=TRANSFORMATIONS, local_dict={"pi": sp.pi, "e": sp.E, "E": sp.E})
    except Exception:  # noqa: BLE001 - a piece that does not parse is not a value
        return None
    if value.is_Float:
        return sp.nsimplify(value, rational=True)
    elif value.is_number:
        return value
    else:
        return None


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
