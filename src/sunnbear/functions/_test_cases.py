"""FormulaTestCase: a formula's declared test cases, colocated with it.

A concrete `Formula` lists `cases` — one `FormulaTestCase` per behavior worth pinning, built via
`FormulaTestCase.value` / `.invalid` / `.bracket`. A single generic test drives every registered
formula through its list, so between them the three kinds cover `parametrized_fun`, both sides of
`is_param_tuple_valid`, and `bracket`; the jit-off branch-coverage gate then fails on any formula
line no case reaches.
"""

from dataclasses import dataclass

# loose enough for the ~1-ulp jit-vs-Python gap, tight enough to catch a real error. atol carries
# the comparison near a root, where `expected` is 0 and a relative tolerance says nothing.
DEFAULT_RTOL = 1e-12
DEFAULT_ATOL = 1e-12


class FormulaTestCase:
    """One declared behavior of a formula. Build via the factory classmethods, never directly."""

    @classmethod
    def value(
        cls,
        params: tuple[float, ...],
        x: float,
        c: float,
        expected: float,
        *,
        rtol: float = DEFAULT_RTOL,
        atol: float = DEFAULT_ATOL,
    ) -> "FormulaTestCase":
        """`f(x, c, *params)` must equal `expected` (and `params` must be accepted as valid)."""
        return ValueTestCase(tuple(params), x, c, expected, rtol, atol)

    @classmethod
    def invalid(cls, params: tuple[float, ...]) -> "FormulaTestCase":
        """`is_param_tuple_valid(*params)` must reject `params`."""
        return InvalidTestCase(tuple(params))

    @classmethod
    def bracket(cls, params: tuple[float, ...], expected: tuple[float, float]) -> "FormulaTestCase":
        """`bracket(*params)` must equal `expected`."""
        return BracketTestCase(tuple(params), expected)


@dataclass(frozen=True)
class ValueTestCase(FormulaTestCase):
    """A point check: `f(x, c, *params)` equals `expected` within `(rtol, atol)`."""

    params: tuple[float, ...]
    x: float
    c: float
    expected: float
    rtol: float
    atol: float


@dataclass(frozen=True)
class InvalidTestCase(FormulaTestCase):
    """A validity check: `is_param_tuple_valid(*params)` returns False."""

    params: tuple[float, ...]


@dataclass(frozen=True)
class BracketTestCase(FormulaTestCase):
    """A bracket check: `bracket(*params)` equals `expected`."""

    params: tuple[float, ...]
    expected: tuple[float, float]
