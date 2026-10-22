"""This module translates a function of the survey into the Python code of a formula, and into a sympy expression.

The survey writes a function in ASCII operators, as 1 expression or as an equation `lhs = rhs`, which the translation
turns into `(lhs) - (rhs)`. Besides the operators, the constants `pi` and `e`, and the functions of `math`, the
translation reads:

- `if(condition; a; b)`: `a` where the condition holds and `b` elsewhere; a condition compares with `<`, `<=`, `>`,
  `>=`, or `=` for equality;
- a comparison in parentheses, as in `(x > 1)`: 1 where it holds and 0 elsewhere. Followed by `*` and an operand, which
  is a bracket, a call, a name or a number, as in `(x > -1)*(1 + sin(1/(x + 1)))`, it gives the operand where the
  comparison holds and 0 elsewhere, and the operand is evaluated only where the comparison holds, so that it may be
  undefined elsewhere;
- `sum(term, i = m..n)` and `prod(term, i = m..n)`, over the integers `i` from `m` to `n`, written out term by term;
- `Phi(z)` and `phi(z)`, the cumulative distribution function and the density of the standard normal distribution;
- `sign`, `cbrt`, and the Bessel functions `J0`, `J1`, `Y0` and `Y1`;
- a power `base^(1/q)` with an odd integer `q`, as the real root, as the sources mean it: negative for a negative base.

Python parses the Python code, and sympy parses a second text that writes the constructs above in sympy's terms. The 2
parsers work independently, so the generator can check the Python code against the sympy expression by their values.
"""

import keyword
import math
import re
from collections.abc import Callable
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from sunnbear._core.utils import math_functions

from .helpers import CONSTANTS, FUNCTIONS, IDENTIFIER, TRANSFORMATIONS

# fmt: off
# PYTHON_FUNCTIONS maps each function name that the translation reads to its Python form: a function of `math`, a
# builtin, or a function of `sunnbear._core.utils.math_functions`.
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
    "sign": "sign", "real_root": "real_root",
    "J0": "bessel_j0", "J1": "bessel_j1", "Y0": "bessel_y0", "Y1": "bessel_y1",
}
# SYMPY_FUNCTIONS maps each function name that the sympy text uses to its sympy form; sympy's own names, such as
# `Piecewise` and `Eq`, need no entry.
SYMPY_FUNCTIONS = {
    **FUNCTIONS,
    "J1": lambda a: sp.besselj(1, a), "Y1": lambda a: sp.bessely(1, a),
}
# fmt: on
# PYTHON_CONSTANTS maps each constant to its Python form; `e` is a constant unless a parameter has its name.
PYTHON_CONSTANTS = {"pi": "math.pi", "e": "math.e"}
# SYMPY_NAMES are the names of sympy's own that the sympy text may hold.
SYMPY_NAMES = {"Piecewise", "Eq", "True"}
# CONSTRUCT_START matches the start of a call that the translation rewrites, or of a bracket that may hold a
# comparison; a bracket right after a name is a call.
CONSTRUCT_START = re.compile(r"(?<![0-9.A-Za-z_])(if|sum|prod|Phi|phi|cbrt)\s*\(|(?<![0-9.A-Za-z_\s])\s*\(|^\(")
# REAL_ROOT_POWER matches the exponent `^(1/q)` of a real root, with an odd `q`.
REAL_ROOT_POWER = re.compile(r"\^\s*\(\s*1\s*/\s*(\d*[13579])\s*\)")
# COMPARISON matches a comparison operator, `=` for equality included.
COMPARISON = re.compile(r"<=|>=|==|!=|<|>|=")
# RANGE matches the range `i = m..n` of a sum or a product.
RANGE = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(-?\d+)\s*\.\.\s*(-?\d+)\s*")
# MULTIPLICATION matches a `*` with the spaces around it, but not a `**`.
MULTIPLICATION = re.compile(r"\s*\*(?!\*)\s*")
# NUMBER matches an unsigned number, such as `2`, `0.5`, `.5` or `1E-4`.
NUMBER = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


class TranslationError(Exception):
    """A `TranslationError` reports a function that the translation cannot read."""


# ==================================================================================================
#  FormulaExpression
# ==================================================================================================
@dataclass(frozen=True)
class FormulaExpression:
    """A `FormulaExpression` holds a survey function as Python code that numba compiles, and as a sympy expression.

    Attributes:
        python_code: The code of 1 Python expression in `x` and in the parameters under their Python names.
        sympy_expr: The same function as a sympy expression in the variable's symbol and in the parameters under
            their survey names.
        variable: The sympy symbol of the function's variable.
    """

    python_code: str
    sympy_expr: sp.Expr
    variable: sp.Symbol

    @property
    def sunnbear_math_functions(self) -> tuple[str, ...]:
        """Return the names of `math_functions.__all__` that the Python code calls, in the order of that list."""
        names = set(IDENTIFIER.findall(self.python_code))
        return tuple(name for name in math_functions.__all__ if name in names)

    def mpmath_function(self, parameter_values: dict[str, sp.Expr]) -> Callable:
        """Return the function of the variable that mpmath evaluates, with the parameters at `parameter_values`.

        Args:
            parameter_values: The value of each parameter, keyed by its survey name.
        """
        values = {sp.Symbol(name): value for name, value in parameter_values.items()}
        return sp.lambdify(self.variable, self.sympy_expr.subs(values), modules="mpmath")

    def python_value(self, x: float, python_values: dict[str, float]) -> float:
        """Return the value of the Python code at `x`, with each parameter's value keyed by its Python name."""
        # the code comes from the translation of the survey's text, which reads only its own names and functions
        return eval(self.python_code, {"math": math, **vars(math_functions)}, {**python_values, "x": x})

    @staticmethod
    def free_names(text: str) -> list[str]:
        """Return the names of a survey function that are neither functions nor `CONSTANTS`, in order of appearance.

        They are the variable and the parameters, and `e` where the function uses it. The index of a sum or a product
        is not free.
        """
        indices = set(re.findall(r",\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*-?\d+\s*\.\.", text))
        names = []
        for match in IDENTIFIER.finditer(text):
            name = match.group(1)
            is_call = text[match.end() :].lstrip().startswith("(")
            if not is_call and name not in indices and name not in CONSTANTS and name not in names:
                names.append(name)
        return names

    # --------------------------------------------------------------------------
    #  Helpers: rewriting the constructs
    # --------------------------------------------------------------------------
    @staticmethod
    def _rewrite_constructs(text: str, target: str) -> str:
        """Return `text` with each construct of the module docstring written for `target`, "python" or "sympy".

        Apart from those constructs, the result keeps the survey's notation; a later step translates its names.
        """
        rewritten = []
        position = 0
        while (match := CONSTRUCT_START.search(text, position)) is not None:
            open_index = match.end() - 1
            close_index = FormulaExpression._matching_bracket(text, open_index)
            name = match.group(1)
            if name is None:
                rewritten.append(text[position:open_index])
                bracket_code, position = FormulaExpression._rewrite_bracket(text, open_index, close_index, target)
                rewritten.append(bracket_code)
            else:
                rewritten.append(text[position : match.start(1)])
                rewritten.append(FormulaExpression._rewrite_call(name, text[open_index + 1 : close_index], target))
                position = close_index + 1
        rewritten.append(text[position:])
        return FormulaExpression._rewrite_real_roots("".join(rewritten), target)

    @staticmethod
    def _rewrite_bracket(text: str, open_index: int, close_index: int, target: str) -> tuple[str, int]:
        """Return the bracket at `open_index`, written for `target`, and the index where the text that it replaces ends.

        A bracket that holds a comparison gives 1 where the comparison holds and 0 elsewhere. Followed by `*` and an
        operand, it gives the operand where the comparison holds and 0 elsewhere, and replaces the operand too: the
        result evaluates the operand only where the comparison holds, so that the operand may be undefined elsewhere,
        as `1/(x + 1)` is at `x = -1`. Any other bracket stays a bracket.
        """
        inner = text[open_index + 1 : close_index]
        operand_span = FormulaExpression._multiplied_operand(text, close_index + 1)
        if not FormulaExpression._top_level_comparisons(inner):
            return f"({FormulaExpression._rewrite_constructs(inner, target)})", close_index + 1
        elif operand_span is not None and target == "python":
            # every operand that `_multiplied_operand` accepts is an atom of Python's grammar once rewritten
            operand = FormulaExpression._rewrite_constructs(text[operand_span[0] : operand_span[1]], target)
            return f"({operand} if {FormulaExpression._rewrite_condition(inner, target)} else 0.0)", operand_span[1]
        elif operand_span is not None:
            operand = FormulaExpression._rewrite_constructs(text[operand_span[0] : operand_span[1]], target)
            return (
                f"Piecewise(({operand}, {FormulaExpression._rewrite_condition(inner, target)}), (0, True))",
                operand_span[1],
            )
        elif target == "python":
            # Python and numba compute with a comparison's bool as 1 or 0, so the bracket stays as published
            return f"({FormulaExpression._rewrite_condition(inner, target)})", close_index + 1
        else:
            return f"Piecewise((1, {FormulaExpression._rewrite_condition(inner, target)}), (0, True))", close_index + 1

    @staticmethod
    def _rewrite_call(name: str, inner: str, target: str) -> str:
        """Return the call `name(inner)` of a construct, written for `target`."""
        if name == "if":
            parts = FormulaExpression._split_top_level(inner, ";")
            if len(parts) != 3:
                raise TranslationError(f"if({inner}) does not hold 3 parts")
            condition = FormulaExpression._rewrite_condition(parts[0], target)
            when_true, when_false = (FormulaExpression._rewrite_constructs(part.strip(), target) for part in parts[1:])
            if target == "python":
                return f"(({when_true}) if {condition} else ({when_false}))"
            else:
                return f"Piecewise(({when_true}, {condition}), ({when_false}, True))"
        elif name in ("sum", "prod"):
            parts = FormulaExpression._split_top_level(inner, ",")
            if len(parts) == 2:
                range_match = RANGE.fullmatch(parts[-1])
            else:
                range_match = None
            if range_match is None:
                raise TranslationError(f"{name}({inner}) has no range of integers `i = m..n`")
            index, start, stop = range_match.group(1), int(range_match.group(2)), int(range_match.group(3))
            term = FormulaExpression._rewrite_constructs(parts[0], target)
            terms = [
                "(" + re.sub(rf"(?<![0-9.A-Za-z_]){index}(?![0-9A-Za-z_])", f"({k})", term) + ")"
                for k in range(start, stop + 1)
            ]
            return "(" + (" + " if name == "sum" else " * ").join(terms) + ")"
        elif name == "cbrt":
            return FormulaExpression._real_root(FormulaExpression._rewrite_constructs(inner, target), 3, target)
        elif name == "Phi" and target == "python":
            return f"(0.5*erfc(-({FormulaExpression._rewrite_constructs(inner, target)})/sqrt(2)))"
        elif name == "Phi":
            return f"((1 + erf(({FormulaExpression._rewrite_constructs(inner, target)})/sqrt(2)))/2)"
        else:
            return f"(exp(-({FormulaExpression._rewrite_constructs(inner, target)})^2/2)/sqrt(2*pi))"

    @staticmethod
    def _rewrite_condition(text: str, target: str) -> str:
        """Return a condition of `if(...)`, 1 comparison, written for `target`: `=` is a test of equality."""
        sides = FormulaExpression._split_comparison(text)
        if sides is None:
            raise TranslationError(f"the condition {text!r} is not 1 comparison")
        lhs, operator, rhs = sides
        lhs = FormulaExpression._rewrite_constructs(lhs.strip(), target)
        rhs = FormulaExpression._rewrite_constructs(rhs.strip(), target)
        if operator in ("=", "==") and target == "python":
            return f"({lhs}) == ({rhs})"
        elif operator in ("=", "=="):
            return f"Eq({lhs}, {rhs})"
        else:
            return f"({lhs}) {operator} ({rhs})"

    @staticmethod
    def _rewrite_real_roots(text: str, target: str) -> str:
        """Return `text` with each power `base^(1/q)` of an odd `q` written as the real root, for `target`."""
        while (match := REAL_ROOT_POWER.search(text)) is not None:
            base_start = FormulaExpression._operand_start(text, match.start())
            base = text[base_start : match.start()].strip()
            real_root = FormulaExpression._real_root(base, int(match.group(1)), target)
            text = text[:base_start] + real_root + text[match.end() :]
        return text

    @staticmethod
    def _real_root(base: str, q: int, target: str) -> str:
        """Return the real `q`-th root of `base`, for an odd `q`, written for `target`."""
        if target == "python":
            return f"real_root({base}, {q})"
        else:
            # `**`, not `^`, so that `REAL_ROOT_POWER` does not match the power again
            return f"(sign({base})*abs({base})**(1/{q}))"

    # --------------------------------------------------------------------------
    #  Helpers: translating the names
    # --------------------------------------------------------------------------
    @staticmethod
    def _translate_names_to_python(code: str, variable: str, python_names: dict[str, str]) -> str:
        """Return `code` with each name in its Python form: the variable as `x`, parameters, functions and constants."""

        def to_python(match: re.Match) -> str:
            """Return the Python form of 1 name of the code."""
            name = match.group(1)
            is_call = code[match.end() :].lstrip().startswith("(")
            if name in ("if", "else"):
                return name
            elif is_call and name in PYTHON_FUNCTIONS:
                return PYTHON_FUNCTIONS[name]
            elif is_call:
                raise TranslationError(f"the function {name} has no Python form")
            elif name == variable:
                return "x"
            elif name in python_names:
                return python_names[name]
            elif name in PYTHON_CONSTANTS:
                return PYTHON_CONSTANTS[name]
            else:
                raise TranslationError(f"the name {name} is neither the variable, a parameter nor a constant")

        return IDENTIFIER.sub(to_python, code)

    @staticmethod
    def _translate_names_to_sympy(text: str, variable: str, python_names: dict[str, str]) -> tuple[str, dict]:
        """Rename each name in `text` that sympy's parser cannot take, and return the renamed text with a dict.

        The dict maps each name of the renamed text to the sympy object that the name stands for. The variable and the
        parameters become symbols of their survey names; `lambda`, a Python keyword, becomes `lambda_`. Only the keys of
        `python_names`, the parameters' survey names, are read.
        """
        local_names: dict = {FormulaExpression._sympy_name(variable): sp.Symbol(variable)}
        for name in IDENTIFIER.findall(text):
            is_call = re.search(rf"(?<![0-9.A-Za-z_]){name}\s*\(", text) is not None
            if name in local_names or name in SYMPY_NAMES:
                continue
            if is_call and name in SYMPY_FUNCTIONS:
                local_names[name] = SYMPY_FUNCTIONS[name]
            elif name in python_names:
                local_names[FormulaExpression._sympy_name(name)] = sp.Symbol(name)
            elif name in CONSTANTS:
                local_names[name] = CONSTANTS[name]
            elif name == "e":
                local_names[name] = sp.E
            else:
                raise TranslationError(f"the name {name} is neither the variable, a parameter nor a constant")
        renamed = IDENTIFIER.sub(lambda match: FormulaExpression._sympy_name(match.group(1)), text)
        return renamed, local_names

    @staticmethod
    def _sympy_name(name: str) -> str:
        """Return the name under which sympy's parser takes a survey name: a Python keyword gets `_` added."""
        if keyword.iskeyword(name) and name != "True":
            return f"{name}_"
        else:
            return name

    # --------------------------------------------------------------------------
    #  Helpers: scanning the text
    # --------------------------------------------------------------------------
    @staticmethod
    def _difference_form(text: str) -> str:
        """Return the function of an equation `lhs = rhs` as `(lhs) - (rhs)`, and any other text as it is.

        Only a top-level `=` makes an equation, not one inside a bracket, such as the condition of `if(x = 0; ...)`.

        Raises:
            TranslationError: If the text has more than 1 top-level `=`.
        """
        sides = FormulaExpression._split_top_level(text, "=")
        if len(sides) == 1:
            return text
        elif len(sides) == 2:
            return f"({sides[0].strip()}) - ({sides[1].strip()})"
        else:
            raise TranslationError(f"{text!r} has several equals signs")

    @staticmethod
    def _split_comparison(text: str) -> tuple[str, str, str] | None:
        """Return a comparison as its 2 sides and its operator, or None if the text is not exactly 1 comparison."""
        comparisons = FormulaExpression._top_level_comparisons(text)
        if len(comparisons) != 1:
            return None
        else:
            match = comparisons[0]
            return text[: match.start()], match.group(0), text[match.end() :]

    @staticmethod
    def _top_level_comparisons(text: str) -> list[re.Match]:
        """Return the comparison operators of `text` that are outside any bracket."""
        depth_at = FormulaExpression._bracket_depths(text)
        return [match for match in COMPARISON.finditer(text) if depth_at[match.start()] == 0]

    @staticmethod
    def _split_top_level(text: str, separator: str) -> list[str]:
        """Split `text` at each `separator` outside any bracket.

        With `=` as the separator, the `=` of `<=`, `>=`, `==` and `!=` does not split.

        Raises:
            TranslationError: If a bracket in `text` does not close.
        """
        depth_at = FormulaExpression._bracket_depths(text)
        parts, start = [], 0
        for i, character in enumerate(text):
            is_part_of_comparison = separator == "=" and (
                text[i - 1 : i] in ("<", ">", "=", "!") or text[i + 1 : i + 2] == "="
            )
            if character != separator or depth_at[i] != 0 or is_part_of_comparison:
                continue
            parts.append(text[start:i])
            start = i + 1
        parts.append(text[start:])
        return parts

    @staticmethod
    def _bracket_depths(text: str) -> list[int]:
        """Return the bracket depth at each character of `text`; a bracket itself is at the depth outside it.

        Raises:
            TranslationError: If a bracket does not close, or closes one that is not open.
        """
        depths, depth = [], 0
        for character in text:
            if character in ")]":
                depth -= 1
            if depth < 0:
                raise TranslationError(f"{text!r} closes a bracket that is not open")
            depths.append(depth)
            if character in "([":
                depth += 1
        if depth != 0:
            raise TranslationError(f"{text!r} leaves a bracket open")
        else:
            return depths

    @staticmethod
    def _matching_bracket(text: str, open_index: int) -> int:
        """Return the index of the bracket that closes the one at `open_index`.

        Raises:
            TranslationError: If the bracket at `open_index` does not close.
        """
        depth = 0
        for i in range(open_index, len(text)):
            if text[i] in "([":
                depth += 1
            elif text[i] in ")]":
                depth -= 1
                if depth == 0:
                    return i
        raise TranslationError(f"{text!r} leaves a bracket open")

    @staticmethod
    def _multiplied_operand(text: str, start: int) -> tuple[int, int] | None:
        """Return the start and end of the operand of a `*` at `start`: a bracket, a call, a name or a number.

        Return None if no `*` follows `start`, after optional spaces, or if no such operand follows the `*`, or if the
        operand is raised to a power, since the `*` then multiplies the power.
        """
        multiplication = MULTIPLICATION.match(text, start)
        if multiplication is None:
            return None
        operand_start = multiplication.end()
        name = IDENTIFIER.match(text, operand_start)
        number = NUMBER.match(text, operand_start)
        if text.startswith("(", operand_start):
            operand_end = FormulaExpression._matching_bracket(text, operand_start) + 1
        elif name is not None and text[name.end() :].lstrip().startswith("("):
            operand_end = FormulaExpression._matching_bracket(text, text.index("(", name.end())) + 1
        elif name is not None:
            operand_end = name.end()
        elif number is not None:
            operand_end = number.end()
        else:
            return None
        if text[operand_end:].lstrip().startswith("^"):
            return None
        else:
            return operand_start, operand_end

    @staticmethod
    def _operand_start(text: str, end: int) -> int:
        """Return where the operand that ends right before `end` starts: a bracket, a call, a name or a number."""
        i = end
        while i > 0 and text[i - 1] == " ":
            i -= 1
        if i > 0 and text[i - 1] == ")":
            depth = 0
            while i > 0:
                i -= 1
                if text[i] == ")":
                    depth += 1
                elif text[i] == "(":
                    depth -= 1
                    if depth == 0:
                        break
        while i > 0 and re.match(r"[A-Za-z0-9_.]", text[i - 1]):
            i -= 1
        return i

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_text(cls, text: str, variable: str, python_names: dict[str, str]) -> "FormulaExpression":
        """Translate a survey function into its Python code and its sympy expression.

        Args:
            text: The function, as the survey writes it.
            variable: The name of the function's variable, which becomes `x` in the Python code.
            python_names: The Python name of each parameter, keyed by its survey name; every other name must be a
                function or a constant.

        Raises:
            TranslationError: If the text holds a construct, a function or a name that the translation does not
                read, or if a parser rejects the result.
        """
        difference_form = cls._difference_form(text)
        python_code = cls._translate_names_to_python(
            cls._rewrite_constructs(difference_form, "python").replace("^", "**"), variable, python_names
        )
        try:
            compile(python_code, "<expression>", "eval")
        except SyntaxError as error:
            raise TranslationError(f"the Python form {python_code!r} does not compile") from error
        sympy_text, local_names = cls._translate_names_to_sympy(
            cls._rewrite_constructs(difference_form, "sympy"), variable, python_names
        )
        try:
            sympy_expr = parse_expr(sympy_text, local_dict=local_names, transformations=TRANSFORMATIONS)
        except Exception as error:  # sympy's parser raises many kinds of errors
            raise TranslationError(f"sympy does not parse {sympy_text!r}: {type(error).__name__}") from error
        return cls(python_code=python_code, sympy_expr=sympy_expr, variable=local_names[cls._sympy_name(variable)])
