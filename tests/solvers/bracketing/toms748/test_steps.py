"""These tests assert that the individual steps of `TOMS748` follow the paper's algorithms and subroutines.

The expected x-values of the first steps on `cubic` are computed in exact rational arithmetic from the x-values and
function values that the solve evaluated, so each solve's x-value equals its expected one up to the rounding of its
own arithmetic.
"""

from fractions import Fraction

import pytest

from sunnbear._core.solvers.core import Interval, SolveState
from sunnbear._core.solvers.core.wrapped_function import WrappedFunction
from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import TOMS748
from tests.solvers.example_functions import cubic


# ==================================================================================================
#  The first steps of the algorithms
# ==================================================================================================
@pytest.mark.parametrize("k", [1, 2])
def test_the_first_step_is_the_secant_step_from_a(k: int):
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so step 4.1.1 evaluates the secant step
    ``c_1 = 1 - f(1) / f[1, 2] = 1 + 1/6``."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values[2] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize("k", [1, 2])
def test_the_step_at_n_2_takes_2_newton_steps_on_the_quadratic_interpolation(k: int):
    """At ``n = 2``, step 4.1.3 calls ``Newton-Quadratic`` with 2 Newton steps, on the interval
    ``[a_2, b_2] = [c_1, 2]`` that ``bracket`` leaves, and on ``d_2 = 1``, the bound that it drops."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    (d_2, fd_2), (b_2, fb_2), (a_2, fa_2) = result.history[:3]
    expected_c_2 = _newton_quadratic_in_exact_arithmetic(a_2, fa_2, b_2, fb_2, d_2, fd_2, 2)
    assert result.evaluated_x_values[3] == pytest.approx(float(expected_c_2), abs=1e-15)


def test_algorithm_4_1_then_takes_the_double_length_secant_step():
    """With ``k = 1``, the x-value evaluated after the x-value of step 4.1.3 is the double-length secant step of steps
    4.1.5 to 4.1.7, ``u - 2*f(u) / f[a_bar, b_bar]``, from the bound ``u`` of ``[c_1, c_2]`` with the smaller ``|f|``,
    which is ``c_2``."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    (a_bar, fa_bar), (u, fu) = [(Fraction(x), Fraction(fx)) for x, fx in result.history[2:4]]
    expected_c_bar = u - 2 * fu / ((fu - fa_bar) / (u - a_bar))
    assert result.evaluated_x_values[4] == pytest.approx(float(expected_c_bar), abs=1e-15)


def test_algorithm_4_2_then_interpolates_through_4_x_values_at_n_2():
    """With ``k = 2``, step 4.2.5 at ``n = 2`` calls ``ipzero`` through the 4 x-values evaluated so far, because the
    step has no exception for ``n = 2``, unlike step 4.2.3; ``e_bar_2`` is ``d_2 = 1``.

    The expected x-value is the zero of the inverse cubic interpolation in its Lagrange form.
    """
    # --- act --------------------------
    result = TOMS748(k=2).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    expected_c_bar = _inverse_cubic_zero_in_exact_arithmetic(result.history[:4])
    assert result.evaluated_x_values[4] == pytest.approx(float(expected_c_bar), abs=1e-15)


# ==================================================================================================
#  The subroutines
# ==================================================================================================
@pytest.mark.parametrize(
    "a, fa, b, fb, d, fd, k, expected_r",
    [
        # x^2 - 2 on [1, 2] with d = 3: A*f(a) < 0, so the Newton steps start from b = 2: 2 -> 3/2 -> 17/12 -> 577/408.
        pytest.param(1.0, -1.0, 2.0, 2.0, 3.0, 7.0, 2, 17.0 / 12.0, id="from_b_2_steps"),
        pytest.param(1.0, -1.0, 2.0, 2.0, 3.0, 7.0, 3, 577.0 / 408.0, id="from_b_3_steps"),
        # x^2 - 2 on [-2, -1] with d = -3: A*f(a) > 0, so the Newton steps start from a = -2: -2 -> -3/2 -> -17/12.
        pytest.param(-2.0, 2.0, -1.0, -1.0, -3.0, 7.0, 2, -17.0 / 12.0, id="from_a_2_steps"),
        # 2x - 1 at 0, 1 and 2: A = 0, so r is the zero of the line through a and b.
        pytest.param(0.0, -1.0, 1.0, 1.0, 2.0, 3.0, 2, 0.5, id="line"),
    ],
)
def test_newton_quadratic_takes_k_newton_steps_on_the_quadratic_through_a_b_and_d(a, fa, b, fb, d, fd, k, expected_r):
    """Where ``f`` is a quadratic, ``P`` is ``f`` itself, and ``Newton-Quadratic`` returns the ``k``-th Newton iterate
    on ``f``, from ``a`` where ``A*f(a) > 0`` and from ``b`` otherwise; where ``A = 0``, it returns the zero of the
    line ``P``.

    The iterates of ``x^2 - 2`` confirm that the Newton step of the paper's equation (4) divides ``P(r)``, not
    ``B(r)``, by the derivative.
    """
    # --- act --------------------------
    r = TOMS748.newton_quadratic(a, fa, b, fb, d, fd, k)

    # --- assert -----------------------
    assert r == pytest.approx(expected_r, abs=1e-15)


def test_ipzero_is_exact_where_the_inverse_function_is_a_cubic():
    """Where ``x`` is a cubic polynomial of ``y = f(x)``, here ``x = 1 + y + y^2 + y^3``, the inverse cubic
    interpolation through 4 points is that polynomial, and ``ipzero`` returns its value at ``y = 0``, which is 1."""
    # --- arrange ----------------------
    # Each point is (x, y), with x = 1 + y + y^2 + y^3 at y = -1, 1, 2 and -2.
    points = [(0.0, -1.0), (4.0, 1.0), (15.0, 2.0), (-5.0, -2.0)]

    # --- act --------------------------
    x_bar = TOMS748.ipzero(*[value for point in points for value in point])

    # --- assert -----------------------
    assert x_bar == pytest.approx(1.0, abs=1e-14)


@pytest.mark.parametrize(
    "a, b, root, c, expected_x, expected_a_bar_b_bar_d",
    [
        # f(a) has the smaller |f| in each case, so u = a = 0, tole(a, b) = tol = 1e-6 and 2*delta = 1.4e-6.
        pytest.param(0.0, 1.0, 0.25, 0.5, 0.5, (0.0, 0.5, 1.0), id="inside"),
        pytest.param(0.0, 1.0, 0.25, 1e-9, 1.4e-6, (1.4e-6, 1.0, 0.0), id="close_to_a"),
        pytest.param(0.0, 1.0, 0.25, 1.0 - 1e-9, 1.0 - 1.4e-6, (0.0, 1.0 - 1.4e-6, 1.0), id="close_to_b"),
        # The interval is at most 4*delta = 2.8e-6 wide, so c becomes the midpoint, whatever its value.
        pytest.param(0.0, 2.5e-6, 0.5e-6, 2e-6, 1.25e-6, (0.0, 1.25e-6, 2.5e-6), id="narrow_interval"),
    ],
)
def test_the_margin_of_bracket_keeps_c_2_delta_inside_the_interval(a, b, root, c, expected_x, expected_a_bar_b_bar_d):
    """On ``f(x) = x - root``, ``bracket`` evaluates ``c`` where it lies at least ``2*delta`` inside ``[a, b]``, moves
    it to ``2*delta`` from a bound that it lies closer to, and takes the midpoint on an interval at most ``4*delta``
    wide, with ``delta = lambda*tole(a, b)``; ``bracket`` returns the part of ``[a, b]`` that holds the sign change,
    and ``d``, the dropped bound."""
    # --- arrange ----------------------
    f = WrappedFunction(lambda x: x - root, max_fevals=10, history_enabled=True)
    fa, fb = f(a), f(b)
    state = SolveState(f=f, interval=Interval.from_interval_bounds(a, b, fa, fb), xtol=1e-6)

    # --- act --------------------------
    a_bar, _, b_bar, _, d, _ = TOMS748(k=1).bracket(state, a, fa, b, fb, c)

    # --- assert -----------------------
    assert f.history[-1][0] == pytest.approx(expected_x, abs=1e-20)
    assert state.x_best == f.history[-1][0]
    assert (a_bar, b_bar, d) == pytest.approx(expected_a_bar_b_bar_d, abs=1e-20)


def test_bracket_keeps_the_sign_change_where_the_product_of_the_paper_underflows():
    """Where ``f(a)`` and ``f(c)`` are tiny and differ in sign, the paper's product ``f(a)f(c)`` underflows to 0, but
    ``bracket``, which compares their signs, keeps ``[a, c]``, which holds the root."""
    # --- arrange ----------------------
    f = WrappedFunction(lambda x: 1e-200 * (x - 0.25), max_fevals=10, history_enabled=False)
    fa, fb = f(0.0), f(1.0)
    state = SolveState(f=f, interval=Interval.from_interval_bounds(0.0, 1.0, fa, fb), xtol=1e-6)

    # --- act --------------------------
    a_bar, _, b_bar, fb_bar, d, _ = TOMS748(k=1).bracket(state, 0.0, fa, 1.0, fb, 0.5)

    # --- assert -----------------------
    assert fa * fb_bar == 0.0
    assert (a_bar, b_bar, d) == (0.0, 0.5, 1.0)


@pytest.mark.parametrize(
    "fa, fb, expected_u",
    [
        pytest.param(-0.5, 1.0, 1.0, id="smaller_at_a"),
        pytest.param(-1.0, 0.5, 3.0, id="smaller_at_b"),
        pytest.param(-1.0, 1.0, 3.0, id="tie"),
    ],
)
def test_tole_takes_u_at_the_bound_with_the_smaller_abs_f_and_at_b_on_a_tie(fa, fb, expected_u):
    """``tole(a, b) = 2*|u|*macheps + tol`` takes ``u`` at the bound of ``[1, 3]`` with the smaller ``|f|``, and at
    ``b`` where both ``|f|`` are equal, the case that the paper leaves open, by the rule of step 4.1.5."""
    # --- act --------------------------
    tole = TOMS748(k=1).tole(1.0, fa, 3.0, fb, 1e-6)

    # --- assert -----------------------
    assert tole == 2.0 * expected_u * FLOAT64_EPS + 1e-6


@pytest.mark.parametrize(
    "values, expected",
    [
        pytest.param((1.0, 2.0, 3.0, 4.0), False, id="distinct"),
        # The paper's product of the 12 differences of these distinct values underflows to 0.
        pytest.param((1e-30, 2e-30, 3e-30, 4e-30), False, id="distinct_and_tiny"),
        *[
            pytest.param(values, True, id=f"equal_{i}_{j}")
            for i, j in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
            for values in [tuple(5.0 if idx in (i, j) else float(idx) for idx in range(4))]
        ],
    ],
)
def test_has_equal_values_compares_the_4_values_pair_by_pair(values, expected):
    """The test ``prod_(i != j) (f_i - f_j) = 0`` of steps 4.1.3, 4.2.3 and 4.2.5 holds exactly where 2 of the 4 values
    are equal, also where the product of their differences would underflow to 0."""
    # --- act / assert -----------------
    assert TOMS748._has_equal_values(*values) is expected


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _newton_quadratic_in_exact_arithmetic(a, fa, b, fb, d, fd, k) -> Fraction:
    """Return the ``r`` of ``Newton-Quadratic(a, b, d, r, k)``, computed by the paper's formulas in exact arithmetic.

    The paper's divided differences are ``f[a, b] = (f(b) - f(a)) / (b - a)`` and
    ``f[a, b, d] = (f[b, d] - f[a, b]) / (d - a)``.
    """
    a, fa, b, fb, d, fd = (Fraction(value) for value in (a, fa, b, fb, d, fd))
    B = (fb - fa) / (b - a)  # noqa: N806 — the paper's name
    A = ((fd - fb) / (d - b) - B) / (d - a)  # noqa: N806 — the paper's name
    if A * fa > 0:
        r = a
    else:
        r = b
    for _ in range(k):
        r = r - (fa + B * (r - a) + A * (r - a) * (r - b)) / (B + A * (2 * r - a - b))
    return r


def _inverse_cubic_zero_in_exact_arithmetic(points: list[tuple[float, float]]) -> Fraction:
    """Return the value at ``y = 0`` of the cubic in ``y`` through the 4 points ``(x, y)``, in exact arithmetic, from
    the Lagrange form of the interpolation."""
    x_zero = Fraction(0)
    for i, (x_i, y_i) in enumerate(points):
        term = Fraction(x_i)
        for j, (_, y_j) in enumerate(points):
            if j != i:
                term *= (0 - Fraction(y_j)) / (Fraction(y_i) - Fraction(y_j))
        x_zero += term
    return x_zero
