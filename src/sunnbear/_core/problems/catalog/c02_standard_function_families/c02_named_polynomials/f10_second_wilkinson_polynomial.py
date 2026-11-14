"""This formula is Wilkinson's second polynomial of degree ``n``, with ``c`` moving its zeros by a common factor."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import is_valid_degree

# Above about degree 44 the values next to the lower bound of the interval underflow. The highest valid degree is a
# round degree below that, which leaves a margin for the values of ``c``.
HIGHEST_VALID_DEGREE = 40
HIGHEST_SWEPT_DEGREE = 20


class SecondWilkinsonPolynomial(Formula):
    """`SecondWilkinsonPolynomial` is the product over ``k = 1..n`` of ``(x - 2^-(k + c))``.

    At ``c = 0`` its zeros are ``2^-1``, ``2^-2``, ..., ``2^-n``. Wilkinson's own second polynomial is the one of
    degree 20.

    ``n`` is the degree, an integer from 1 to `HIGHEST_VALID_DEGREE`. The function has ``n`` zeros in its interval for
    an odd ``n``, and ``n - 1`` for an even ``n``, whose interval leaves out the lowest zero.

    The zeros lie closer together toward the lower bound of the interval, each half as far from 0 as the one above
    it. The values of the function between the zeros get smaller toward that bound, so the range of values grows much
    faster with ``n`` than in `WilkinsonPolynomial`.

    ``c`` moves every zero by the same factor, ``2^-c``. In `WilkinsonPolynomial` the zeros are ``k + c``; here they
    are ``2^-(k + c)``.

    A shift of ``x`` does not work here: the lowest zeros lie about ``2^-n`` apart, so the calibrated range of ``c``
    would be so narrow that the values of ``c`` that a benchmark samples would hardly differ.

    References:
        - Wilkinson, J. H. (1959). The evaluation of the zeros of ill-conditioned polynomials. Part I. Numerische
          Mathematik 1, 150-166. https://doi.org/10.1007/BF01386381
        - Wilkinson, J. H. (1963). Rounding Errors in Algebraic Processes. Prentice-Hall.
    """

    number = (2, 2, 10)
    name = "Second Wilkinson polynomial"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the product over ``k = 1..n`` of ``(x - 2^-(k + c))``, 1 factor at a time."""
        zero_k = 2.0 ** (-c)
        value = 1.0
        for _ in range(int(n)):
            zero_k *= 0.5
            value *= x - zero_k
        return value

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return ``[2^-(n + 1), 1]`` for an odd ``n``, and ``[2^-(n - 0.5), 1]`` for an even ``n``.

        The bounds ``2^-(n + 1)`` and 1 lie a factor 2 beyond the outermost zeros. The bound ``2^-(n - 0.5)`` is the
        geometric mean of the 2 lowest zeros, ``2^-n`` and ``2^-(n - 1)``.
        """
        if int(n) % 2 == 1:
            return (2.0 ** -(n + 1.0), 1.0)
        else:
            return (2.0 ** -(n - 0.5), 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps every degree from 1 to `HIGHEST_SWEPT_DEGREE`.

        The sweep ends at the degree of Wilkinson's own second polynomial. This formula's range of values is far wider
        than that of the category's other formulas, and a higher degree would widen it further.
        """
        return (ParamGrid.decimal("n", 1.0, float(HIGHEST_SWEPT_DEGREE), 1.0),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer from 1 to `HIGHEST_VALID_DEGREE`."""
        if not is_valid_degree(n):
            return False
        else:
            return n <= HIGHEST_VALID_DEGREE

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=1.0, c=0.0, expected=0.5),  # x - 0.5
        FormulaTestCase.value(params={"n": 1.0}, x=1.0, c=1.0, expected=0.75),  # c = 1 halves the zero, to 0.25
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=0.0, expected=0.375),  # (x - 0.5)*(x - 0.25)
        FormulaTestCase.value(params={"n": 2.0}, x=0.375, c=0.0, expected=-0.015625),  # between the 2 zeros
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 41.0}),  # degree above the highest one
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.25, 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(2.0**-1.5, 1.0)),
    )
