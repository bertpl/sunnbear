"""This formula is Wilkinson's polynomial of degree ``n``, divided by ``n!``, with ``x`` shifted by ``c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import is_valid_degree

HIGHEST_SWEPT_DEGREE = 40


class WilkinsonPolynomial(Formula):
    """`WilkinsonPolynomial` is the product over ``k = 1..n`` of ``(x - c - k)/k``.

    At ``c = 0`` its zeros are 1, 2, ..., ``n``. Wilkinson's own polynomial is the one of degree 20.

    ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``, and
    ``n - 1`` for an even ``n``, whose interval leaves out the zero at 1.

    The amplitude is largest next to the bounds of the interval and smallest in its middle, and the ratio between
    the 2 grows quickly with ``n``.

    The function is a product, and `parametrized_fun` evaluates it as one. Wilkinson's polynomial is known for its
    expanded form, in which rounding errors make the computed values noisy near the zeros. The product has no such
    noise, and a function with noise belongs to another category.

    Each factor is divided by ``k``, which divides the polynomial by ``n!``: the function is then 1 at the upper
    bound for every ``n``. The division moves no zero, because it only scales the function.

    ``c`` shifts ``x`` by ``c`` itself, not by ``c/n^2`` as in the formulas whose polynomials are orthogonal on
    ``[-1, 1]``, because the zeros lie 1 apart for every ``n``.

    References:
        - Wilkinson, J. H. (1959). The evaluation of the zeros of ill-conditioned polynomials. Part I. Numerische
          Mathematik 1, 150-166. https://doi.org/10.1007/BF01386381
        - Wilkinson, J. H. (1963). Rounding Errors in Algebraic Processes. Prentice-Hall.
    """

    number = (2, 2, 9)
    name = "Wilkinson polynomial"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the product over ``k = 1..n`` of ``(x - c - k)/k``, 1 factor at a time."""
        y = x - c
        value = 1.0
        for k in range(1, int(n) + 1):
            value *= (y - k) / k
        return value

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return ``[0, n + 1]`` for an odd ``n``, and ``[1.5, n + 1]`` for an even ``n``.

        The bounds 0 and ``n + 1`` lie 1 beyond the outermost zeros, and the bound 1.5 lies midway between the 2
        lowest zeros.
        """
        if int(n) % 2 == 1:
            return (0.0, n + 1.0)
        else:
            return (1.5, n + 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps every degree from 1 to `HIGHEST_SWEPT_DEGREE`.

        A higher degree mainly adds a wider range of values between the middle of the interval and its bounds, and
        such ranges are left to formulas that are built for them.
        """
        return (ParamGrid.decimal("n", 1.0, float(HIGHEST_SWEPT_DEGREE), 1.0),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer of at least 1."""
        return is_valid_degree(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.25, c=0.0, expected=-0.75),  # y - 1
        FormulaTestCase.value(params={"n": 2.0}, x=1.5, c=0.0, expected=-0.125),  # (y - 1)*(y - 2)/2
        FormulaTestCase.value(params={"n": 2.0}, x=2.0, c=0.5, expected=-0.125),  # c shifts x to y = 1.5
        FormulaTestCase.value(params={"n": 3.0}, x=4.0, c=0.0, expected=1.0),  # 1 at the upper bound
        FormulaTestCase.value(params={"n": 3.0}, x=0.0, c=0.0, expected=-1.0),  # -1 at the lower bound of an odd n
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 0.0}),  # degree below 1
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(0.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"n": 20.0}, expected=(1.5, 21.0)),
    )
