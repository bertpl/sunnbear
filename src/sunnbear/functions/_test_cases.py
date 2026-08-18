"""FormulaTestCase: a formula's self-declared test cases.

A concrete `Formula` lists `cases` — one `FormulaTestCase` per behavior worth pinning, built via
`FormulaTestCase.value` / `.invalid` / `.bracket`. A single generic test drives every registered
formula through its list, so between them the three kinds cover `parametrized_fun`, both sides of
`is_param_tuple_valid`, and `bracket`; the branch-coverage gate then fails on any formula line no
case reaches.

Parameters are given by name (`{"p1": 0.0}`) and resolved to positional order against the formula's
`param_names` when a case runs.
"""

from dataclasses import dataclass

# The defaults are loose enough for the ~1-ulp jit-vs-Python gap but tight enough to catch a real
# error; atol matters near a root, where `expected` is 0 and a relative tolerance says nothing.
DEFAULT_RTOL = 1e-12
DEFAULT_ATOL = 1e-12


class FormulaTestCase:
    """One self-declared behavior of a formula. Build via the factory classmethods, never directly."""

    @classmethod
    def value(
        cls,
        params: dict[str, float],
        x: float,
        c: float,
        expected: float,
        *,
        rtol: float = DEFAULT_RTOL,
        atol: float = DEFAULT_ATOL,
    ) -> "FormulaTestCase":
        """`f(x, c, *params)` must equal `expected` (and `params` must be accepted as valid)."""
        return ValueTestCase(params, x, c, expected, rtol, atol)

    @classmethod
    def invalid(cls, params: dict[str, float]) -> "FormulaTestCase":
        """`is_param_tuple_valid(*params)` must reject `params`."""
        return InvalidTestCase(params)

    @classmethod
    def bracket(
        cls,
        params: dict[str, float],
        expected: tuple[float, float],
        *,
        rtol: float = DEFAULT_RTOL,
        atol: float = DEFAULT_ATOL,
    ) -> "FormulaTestCase":
        """`bracket(*params)` must equal `expected` within `(rtol, atol)`."""
        return BracketTestCase(params, expected, rtol, atol)


@dataclass(frozen=True)
class ValueTestCase(FormulaTestCase):
    """A point check: `f(x, c, *params)` equals `expected` within `(rtol, atol)`."""

    params: dict[str, float]
    x: float
    c: float
    expected: float
    rtol: float
    atol: float


@dataclass(frozen=True)
class InvalidTestCase(FormulaTestCase):
    """A validity check: `is_param_tuple_valid(*params)` returns False."""

    params: dict[str, float]


@dataclass(frozen=True)
class BracketTestCase(FormulaTestCase):
    """A bracket check: `bracket(*params)` equals `expected` within `(rtol, atol)`."""

    params: dict[str, float]
    expected: tuple[float, float]
    rtol: float
    atol: float
