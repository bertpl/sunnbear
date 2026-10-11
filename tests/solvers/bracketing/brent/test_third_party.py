"""These tests assert that `Brent` reproduces third parties' published results for it:

- the evaluation counts and bisection switches of the column "Brent's" of Table 2 of Chandrupatla (1997);
- the evaluation counts of the column "BR" of Tables II and IV to VI of Alefeld, Potra and Shi (1995);
- the iteration counts of the column "Brent" of Examples 1 to 7 of Anderson and Björck (1973), in single precision.

Each paper ran Brent's procedure ``zero`` with its stopping rule, so `Brent` runs with only its tolerance ``t`` set to
the paper's.
"""

import pytest

from sunnbear.solvers import Brent
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import ALEFELD_POTRA_SHI_PROBLEMS

from .third_party_problems import (
    ALEFELD_POTRA_SHI_TABLES_IV_TO_VI,
    ANDERSON_BJORCK_EXAMPLES_SINGLE_PRECISION,
    CHANDRUPATLA_TABLE_2,
    CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES,
)
from .tolerance import xtol_for_t

# Chandrupatla's tolerance is ``2 * eps_R * |x| + 0.5 * eps_A``, with the absolute tolerance ``eps_A = 1e-5``, so
# Brent's ``t`` is ``0.5 * eps_A``.
_CHANDRUPATLA_T = 0.5e-5


@pytest.mark.parametrize("problem", CHANDRUPATLA_TABLE_2, ids=str)
def test_the_evaluation_counts_of_chandrupatla_table_2_are_reproduced(problem: PaperProblem):
    """On every row of Table 2 of Chandrupatla (1997), `Brent` evaluates exactly as often as the column "Brent's"
    reports.

    The paper also sets a relative tolerance of 1e-10 in place of Brent's machine precision; it makes no difference to
    these counts.
    """
    # --- act --------------------------
    result = Brent().solve(
        problem.f, problem.a, problem.b, xtol=xtol_for_t(_CHANDRUPATLA_T, problem.a, problem.b), max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem, n_bisection_switches", CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES, ids=str)
def test_the_bisection_switch_counts_of_chandrupatla_table_2_are_reproduced(
    problem: PaperProblem, n_bisection_switches: int
):
    """On every row of Table 2 of Chandrupatla (1997), `Brent` bisects exactly as often as the column "Brent's" reports
    in parentheses."""
    # --- act --------------------------
    result = Brent().solve(
        problem.f,
        problem.a,
        problem.b,
        xtol=xtol_for_t(_CHANDRUPATLA_T, problem.a, problem.b),
        max_fevals=300,
        history_enabled=True,
    )

    # --- assert -----------------------
    assert _count_bisections(result.history) == n_bisection_switches


@pytest.mark.parametrize("problem", ALEFELD_POTRA_SHI_TABLES_IV_TO_VI, ids=str)
def test_the_evaluation_counts_of_alefeld_potra_shi_tables_iv_to_vi_are_reproduced(problem: PaperProblem):
    """On every problem of Tables IV to VI of Alefeld, Potra and Shi (1995), `Brent` with ``t = 10^-15`` evaluates as
    often as the column "BR" reports, except where the problem states an allowed deviation."""
    # --- act --------------------------
    result = Brent().solve(
        problem.f, problem.a, problem.b, xtol=xtol_for_t(1e-15, problem.a, problem.b), max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("t, paper_total", [(1e-7, 2804), (1e-10, 2905), (1e-15, 2975), (0.0, 3008)])
def test_the_total_evaluation_count_lies_within_1_percent_of_alefeld_potra_shi_table_ii(t: float, paper_total: int):
    """Over all 154 problems of Alefeld, Potra and Shi (1995), the total evaluation count of `Brent` lies within 1 % of
    the column "BR" of the paper's Table II, for each of the paper's tolerances.

    The paper's counts include the 2 evaluations at the interval bounds, and come from a machine whose relative
    precision was 1.907e-16, not 2^-52.
    """
    # --- arrange / act ----------------
    total = sum(
        Brent()
        .solve(problem.f, problem.a, problem.b, xtol=xtol_for_t(t, problem.a, problem.b), max_fevals=1000)
        .n_fevals
        for problem in ALEFELD_POTRA_SHI_PROBLEMS
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.01 * paper_total


@pytest.mark.parametrize("problem", ANDERSON_BJORCK_EXAMPLES_SINGLE_PRECISION, ids=str)
def test_the_iteration_counts_of_anderson_bjorck_examples_1_to_7_are_reproduced(problem: PaperProblem):
    """On every case of Examples 1 to 7 of Anderson and Björck (1973), `Brent` with ``t = 6e-8``, the paper's tolerance
    in single precision, takes as many iterations as the column "Brent" reports, except where the problem states an
    allowed deviation.

    The paper sets the relative part of Brent's tolerance to 0; in float64, that part, ``2 * macheps * |b|`` with every
    root in ``[0, 1]``, makes no difference to these counts.
    """
    # --- act --------------------------
    result = Brent().solve(problem.f, problem.a, problem.b, xtol=xtol_for_t(6e-8, problem.a, problem.b), max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _count_bisections(history: tuple[tuple[float, float], ...]) -> int:
    """Return the number of iterations of a `Brent` solve that evaluate the midpoint of the interval.

    ``history`` holds every ``(x, f(x))`` of the solve, in order, starting with the evaluations at ``a`` and ``b``. The
    function follows Brent's bounds ``b`` and ``c`` through the history, as `Brent` keeps them: ``b`` is the bound with
    the smaller ``|f|``, and ``c`` the bound on the other side of the root.

    A bisection is the only step that evaluates ``b + (c - b) / 2`` exactly: the tolerance step moves at most
    ``tol`` from ``b``, less than half the interval while the solve runs, and an interpolation step to exactly the
    midpoint does not occur on the rows of Table 2.
    """
    # The Algol label "int": c starts as a, the bound on the other side of the root from b.
    (c, fc), (b, fb) = history[0], history[1]
    n_bisections = 0
    for x, fx in history[2:]:
        # The Algol label "ext": b becomes the bound with the smaller |f|.
        if abs(fc) < abs(fb):
            b, c = c, b
            fb, fc = fc, fb
        if x == b + 0.5 * (c - b):
            n_bisections += 1
        previous_b, previous_fb = b, fb
        b, fb = x, fx
        if (fb > 0.0) == (fc > 0.0):
            # b crossed the root, so its previous value becomes c.
            c, fc = previous_b, previous_fb
    return n_bisections
