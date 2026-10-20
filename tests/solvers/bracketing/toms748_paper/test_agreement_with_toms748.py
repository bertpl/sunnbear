"""These tests compare `TOMS748Paper` with `TOMS748`, which follows the authors' Fortran code, to show that the 2
implementations take the same steps, and differ only in the places listed below.

In 60-digit arithmetic, formulas that are equal in exact arithmetic give the same x-value to far below the float64
spacing. At 60 digits, both implementations pass the same float64 x-values to ``f`` on every solve of
`_COMPARED_SOLVES`.

In float64, the 2 implementations differ in these places:

- **Formula forms that round differently:**

  - the secant step 4.1.1 starts from ``a``, and the double-length secant step 4.1.6 from ``u``; with ``x`` the
    x-value that each step starts from, `TOMS748` computes the step as ``(f(x) / (f(b) - f(a)))*(b - a)``, where
    `TOMS748Paper` computes ``f(x) / f[a, b]``;
  - `TOMS748` computes each midpoint as ``a + 0.5*(b - a)``, where `TOMS748Paper` computes ``0.5*(a + b)``;
  - in ``Newton-Quadratic``, `TOMS748` computes ``P(x)`` as ``f(a) + (B + A*(x - b))*(x - a)``, and its derivative
    with ``(2*x) - (a + b)``, where `TOMS748Paper` computes ``f(a) + B*(x - a) + A*(x - a)*(x - b)``, and
    ``2*x - a - b``;
  - in ``ipzero``, `TOMS748` computes each quantity such as ``Q11`` as ``((c - d)*f(c)) / (f(d) - f(c))``, where
    `TOMS748Paper` computes ``(c - d)*(f(c) / (f(d) - f(c)))``.
- **Tests written as products:** `TOMS748` computes the products ``prod_(i != j) (f_i - f_j)`` and
  ``(c - a)*(c - b)``, which can underflow to 0, where `TOMS748Paper` compares their factors.
- **A zero derivative in** ``Newton-Quadratic``: where a Newton step meets ``P'(x) = 0``, `TOMS748` returns the zero
  of the line through ``a`` and ``b``, where `TOMS748Paper` divides by 0, and the solve ends as ``SOLVER_ERROR``. In
  exact arithmetic, the derivative never vanishes on these steps, so only rounding can lead to this case.
- **A stopping check before the first step:** `TOMS748` also checks the stopping criterion at the start of each
  iteration, where the authors' code checks it, and `TOMS748Paper` only after each call of ``bracket``, where the paper
  checks it. On an initial interval at most ``2*xtol`` wide, `TOMS748` then ends the solve after the 2 evaluations at
  the interval bounds, and `TOMS748Paper` after 3; on any other interval, the extra check changes only the flop counts.
- **Flop counts:** the forms and the extra check above make every solve's flop counts differ.
"""

import mpmath
import pytest

from sunnbear._core.solvers.bracketing.toms748_paper import TOMS748Paper
from sunnbear.benchmark import compute_xtol_range
from sunnbear.solvers import TOMS748, Interval, Solver, SolveState
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES, cubic
from tests.solvers.paper_problems.alefeld_potra_shi import ALEFELD_POTRA_SHI_PROBLEMS
from tests.solvers.twins import TWIN_TEST_CASES

# At 60 digits, each x-value has about 200 bits, so that 2 forms of 1 formula round to the same float64 x-value,
# except where the formula's exact value lies less than about 10^-44 float spacings from a value halfway between 2
# float64 values.
_N_DIGITS = 60

# No compared solve reaches this budget.
_MAX_FEVALS = 400

# Each compared solve is a tuple (label, f, a, b, xtol). On the problems of the authors' test output, xtol is 1.5
# times the smallest xtol at which bisection spends n evaluations.
_COMPARED_SOLVES = [
    *[
        (f"{problem.name}@{n}", problem.f, problem.a, problem.b, 1.5 * xtol_min)
        for problem in ALEFELD_POTRA_SHI_PROBLEMS
        for n in (10, 20, 30, 40)
        for xtol_min, _ in [compute_xtol_range(a=problem.a, b=problem.b, n_bisection_fevals=n)]
    ],
    *[(f"{param.id}@{xtol:g}", *param.values[:3], xtol) for param in CONVERGENCE_TEST_CASES for xtol in (1e-4, 1e-10)],
    *[(str(test_case), test_case.f, test_case.a, test_case.b, test_case.xtol) for test_case in TWIN_TEST_CASES],
]


@pytest.mark.parametrize("k", [1, 2])
@pytest.mark.parametrize(
    "f, a, b, xtol",
    [pytest.param(f, a, b, xtol, id=label) for label, f, a, b, xtol in _COMPARED_SOLVES],
)
def test_in_60_digit_arithmetic_both_implementations_evaluate_the_same_x_values(f, a, b, xtol, k: int):
    """In 60-digit arithmetic, `TOMS748Paper` and `TOMS748` pass the same float64 x-values to ``f``, in the same order,
    and return the same root estimate."""
    # --- act --------------------------
    x_values_toms748_paper, x_root_toms748_paper = _solve_in_60_digit_arithmetic(TOMS748Paper(k=k), f, a, b, xtol)
    x_values_toms748, x_root_toms748 = _solve_in_60_digit_arithmetic(TOMS748(k=k), f, a, b, xtol)

    # --- assert -----------------------
    assert x_values_toms748_paper == x_values_toms748
    assert x_root_toms748_paper == x_root_toms748


@pytest.mark.parametrize("k", [1, 2])
def test_on_an_initial_interval_at_most_2_xtol_wide_toms748_paper_takes_1_evaluation_more(k: int):
    """On an initial interval at most ``2*xtol`` wide, `TOMS748` ends the solve after the 2 evaluations at the interval
    bounds, and `TOMS748Paper` after 3, because it checks the stopping criterion only after each call of
    ``bracket``."""
    # --- arrange ----------------------
    a, b, xtol = 1.32471795, 1.32471796, 1e-8

    # --- act --------------------------
    n_fevals_toms748_paper = TOMS748Paper(k=k).solve(cubic, a, b, xtol=xtol, max_fevals=10).n_fevals
    n_fevals_toms748 = TOMS748(k=k).solve(cubic, a, b, xtol=xtol, max_fevals=10).n_fevals

    # --- assert -----------------------
    assert (n_fevals_toms748_paper, n_fevals_toms748) == (3, 2)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _solve_in_60_digit_arithmetic(solver: Solver, f, a: float, b: float, xtol: float) -> tuple[list[float], float]:
    """Return the float64 x-values that ``solver`` passes to ``f`` in 60-digit arithmetic, and its root estimate.

    The solve calls the solver's `Solver._solve` directly, on `mpmath.mpf` interval bounds and function values, so
    that all of its arithmetic runs at 60 digits. ``f`` itself receives each x-value rounded to float64.
    """
    x_values: list[float] = []

    def f_recorded(x: mpmath.mpf) -> mpmath.mpf:
        """Return ``f`` at ``x`` rounded to float64, and record that x-value."""
        assert len(x_values) < _MAX_FEVALS
        x_values.append(float(x))
        return mpmath.mpf(f(float(x)))

    with mpmath.workdps(_N_DIGITS):
        interval = Interval.from_interval_bounds(mpmath.mpf(a), mpmath.mpf(b), mpmath.mpf(f(a)), mpmath.mpf(f(b)))
        # `SolveState` normally holds a `WrappedFunction`, which rounds each value to float64; `f_recorded` takes its
        # place here, so that the solver's values stay at 60 digits.
        state = SolveState(f=f_recorded, interval=interval, xtol=mpmath.mpf(xtol))  # type: ignore[arg-type]
        x_root = float(solver._solve(state))
    return x_values, x_root
