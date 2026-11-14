"""This formula is the Chebyshev polynomial of the second kind with ``x`` shifted by ``c``, ``U_n(x - c/n^2)``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import degree_sweep_recipe, is_valid_degree, jacobi_interval_bounds


class ChebyshevSecondKindPolynomial(Formula):
    """`ChebyshevSecondKindPolynomial` is ``U_n(x - c/n^2)``, with ``U_n`` the Chebyshev polynomial of the second kind.

    The swings of ``U_n`` grow from about 1 in the middle of ``[-1, 1]`` to ``n + 1`` at the bounds -1 and 1.

    - ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``,
      and ``n - 1`` for an even ``n``.

    ``c`` shifts ``x``, so the function keeps its form and every zero of its interval for every ``c``. Adding ``c`` to
    the function value would not keep them: the range of ``c`` would follow the values at the bounds, which grow with
    ``n``, and nearly every ``c`` of a high degree would leave only the zero in the outermost swing. The shift is
    ``c/n^2`` because the zeros next to the bounds lie about ``1/n^2`` apart.

    `parametrized_fun` evaluates ``U_n(y)`` from ``abs(y)``, since ``U_n(-y) = (-1)^n * U_n(y)``:

    - inside ``(-1, 1)``, as ``sin((n + 1)*t)/sin(t)`` with ``t = acos(abs(y))``, which costs the same for every ``n``;
    - at -1 and 1, as ``n + 1``, because the form above is 0/0 there;
    - beyond -1 and 1, where the shift takes ``y`` by a few times ``1/n^2``, as ``sinh((n + 1)*t)/sinh(t)`` with
      ``t = acosh(abs(y))``.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition, and §18.5(i), for the
          trigonometric form. https://dlmf.nist.gov/18.3 and https://dlmf.nist.gov/18.5
    """

    number = (2, 2, 2)
    name = "Chebyshev polynomial of the second kind"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``U_n(x - c/n^2)``."""
        y = x - c / (n * n)
        abs_y = abs(y)
        if abs_y < 1.0:
            t = math.acos(abs_y)
            value_at_abs_y = math.sin((n + 1.0) * t) / math.sin(t)
        elif abs_y == 1.0:
            value_at_abs_y = n + 1.0
        else:
            t = math.acosh(abs_y)
            value_at_abs_y = math.sinh((n + 1.0) * t) / math.sinh(t)
        if y < 0.0 and int(n) % 2 == 1:
            return -value_at_abs_y
        else:
            return value_at_abs_y

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return ``[-1, 1]`` for an odd ``n``, and ``[-cos(1.5*pi/(n + 1)), 1]`` for an even ``n``.

        ``U_n`` is the Jacobi polynomial with both parameters 0.5, up to a constant factor.
        """
        return jacobi_interval_bounds(n, 0.5, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps the degrees of `SWEPT_DEGREES`."""
        return (degree_sweep_recipe(self.param_names),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer of at least 1."""
        return is_valid_degree(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.75, c=0.0, expected=1.25),  # U_2(y) = 4*y^2 - 1
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=1.0, expected=1.25),  # c shifts x by c/4, to y = 0.75
        FormulaTestCase.value(params={"n": 3.0}, x=-0.5, c=0.0, expected=1.0),  # U_3(y) = 8*y^3 - 4*y, an odd function
        FormulaTestCase.value(params={"n": 3.0}, x=1.0, c=0.0, expected=4.0),  # U_n(1) = n + 1
        FormulaTestCase.value(params={"n": 3.0}, x=-1.0, c=0.0, expected=-4.0),  # U_n(-1) = (-1)^n * (n + 1)
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=-4.0, expected=15.0),  # beyond 1, at y = 2
        FormulaTestCase.value(params={"n": 3.0}, x=-1.0, c=9.0, expected=-56.0),  # beyond -1, at y = -2
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 0.0}),  # degree below 1
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 4.0}, expected=(-math.cos(0.3 * math.pi), 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
