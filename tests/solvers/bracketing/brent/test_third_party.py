"""These tests assert that `Brent` reproduces third parties' published results for it:

- the evaluation counts and bisection switches of the column "Brent's" of Table 2 of Chandrupatla (1997);
- the evaluation counts of the column "BR" of Tables II and IV to VI of Alefeld, Potra and Shi (1995);
- the iteration counts of the column "Brent" of Examples 1 to 7 of Anderson and Björck (1973), in single precision;
- the evaluation counts and roots of the column "Bre" of Table 2 of Ganchovski et al. (2026).

Each paper ran Brent's procedure ``zero``, stopping rule included, so the tests set only the tolerance ``t`` of
`Brent` to the paper's value. Ganchovski et al. ran a version whose tolerance has a larger relative part, which the
test maps onto ``t``.
"""

import pytest

from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import Brent
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import (
    ALEFELD_POTRA_SHI_PROBLEMS,
    AlefeldPotraShiTablesIVToVIProblem,
)
from tests.solvers.paper_problems.anderson_bjorck import AndersonBjorckExampleProblem
from tests.solvers.paper_problems.chandrupatla import ChandrupatlaTable2Problem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem

from .third_party_problems import (
    ALEFELD_POTRA_SHI_TABLES_IV_TO_VI,
    ANDERSON_BJORCK_EXAMPLES_1_TO_7,
    CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES,
    GANCHOVSKI_ET_AL_TABLE_2,
)
from .tolerance import xtol_for_t

# Chandrupatla's tolerance is ``2 * eps_R * |x| + 0.5 * eps_A``, with the absolute tolerance ``eps_A = 1e-5``, so
# Brent's ``t`` is ``0.5 * eps_A``.
_CHANDRUPATLA_T = 0.5e-5


@pytest.mark.parametrize(
    "problems, table",
    [
        pytest.param(
            [problem for problem, _ in CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES],
            ChandrupatlaTable2Problem,
            id="chandrupatla_table_2",
        ),
        pytest.param(ALEFELD_POTRA_SHI_TABLES_IV_TO_VI, AlefeldPotraShiTablesIVToVIProblem, id="alefeld_potra_shi"),
        pytest.param(ANDERSON_BJORCK_EXAMPLES_1_TO_7, AndersonBjorckExampleProblem, id="anderson_bjorck"),
        pytest.param(GANCHOVSKI_ET_AL_TABLE_2, GanchovskiEtAlTable2Problem, id="ganchovski_et_al"),
    ],
)
def test_each_published_column_names_every_problem_of_its_table_in_order(problems, table):
    """Each column of `Brent`'s published counts holds 1 problem per member of its table's enum, in the table's
    order."""
    # --- assert -----------------------
    assert [problem.name for problem in problems] == [member.value.name for member in table]


@pytest.mark.parametrize("problem", [problem for problem, _ in CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES], ids=str)
def test_the_evaluation_counts_of_chandrupatla_table_2_are_reproduced(problem: PaperProblem):
    """On every row of Table 2 of Chandrupatla (1997), `Brent` evaluates exactly as often as the column "Brent's"
    reports.

    The paper also sets a relative tolerance of 1e-10 in place of the machine precision in Brent's tolerance; that
    substitution makes no difference to these counts.
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
    assert _count_bisection_switches(result.history) == n_bisection_switches


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
    """Over all problems of `ALEFELD_POTRA_SHI_PROBLEMS`, the total evaluation count of `Brent` lies within 1 % of
    the column "BR" of the paper's Table II, for each of the paper's tolerances.

    The paper's counts include the 2 evaluations at the interval bounds. They come from a machine whose relative
    precision was 1.907e-16, not 2^-52, so the test compares the totals within 1 %, not exactly.
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


@pytest.mark.parametrize("problem", ANDERSON_BJORCK_EXAMPLES_1_TO_7, ids=str)
def test_the_iteration_counts_of_anderson_bjorck_examples_1_to_7_are_reproduced(problem: PaperProblem):
    """On every case of Examples 1 to 7 of Anderson and Björck (1973), `Brent` with ``t = 6e-8``, the paper's tolerance
    in single precision, takes as many iterations as the column "Brent" reports, except where the problem states an
    allowed deviation.

    The paper sets the relative part of Brent's tolerance, ``2 * macheps * |b|``, to 0. `Brent` keeps that part, but
    with every root in ``[0, 1]`` that part is at most 4.4e-16 in float64 and makes no difference to these counts.
    """
    # --- act --------------------------
    result = Brent().solve(problem.f, problem.a, problem.b, xtol=xtol_for_t(6e-8, problem.a, problem.b), max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem", GANCHOVSKI_ET_AL_TABLE_2, ids=str)
def test_the_evaluation_counts_and_roots_of_ganchovski_et_al_table_2_are_reproduced(problem: PaperProblem):
    """On every row of Table 2 of Ganchovski et al. (2026), `Brent` with the paper's tolerance evaluates as often as
    the column "Bre" reports, except where the problem states an allowed deviation, and returns the root that the
    paper's supplementary results give."""
    # --- act --------------------------
    result = Brent().solve(
        problem.f, problem.a, problem.b, xtol=_xtol_for_ganchovski_et_al_tolerance(problem), max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _xtol_for_ganchovski_et_al_tolerance(problem: PaperProblem) -> float:
    """Return the ``xtol`` under which `Brent` stops by the tolerance of Ganchovski et al.'s C# code on ``problem``.

    The C# code replaces the tolerance ``tol = 2 * macheps * |b| + t`` of Brent's procedure ``zero`` by
    ``(aTol + rTol * |b|) / 2``, with ``aTol = rTol = 1e-14``. That equals ``tol`` for
    ``t = 0.5e-14 + (0.5e-14 - 2 * macheps) * |b|``. The solve stops with ``b`` within ``tol`` of the root, so ``|b|``
    is taken as the absolute value of the published root.
    """
    assert problem.root is not None
    t = 0.5e-14 + (0.5e-14 - 2.0 * FLOAT64_EPS) * abs(problem.root)
    return xtol_for_t(t, problem.a, problem.b)


def _count_bisection_switches(history: tuple[tuple[float, float], ...]) -> int:
    """Return the number of iterations of a `Brent` solve that evaluate the midpoint of the interval.

    ``history`` holds every ``(x, f(x))`` of the solve, in order, starting with the evaluations at ``a`` and ``b``.

    The function follows Brent's bounds ``b`` and ``c`` through the history, as `Brent` keeps them: ``b`` is the bound
    with the smaller ``|f|``, and ``c`` the bound on the other side of the root.

    A bisection is the only step that evaluates ``b + (c - b) / 2`` exactly:

    - the step that Brent's method takes when an interpolated step would be shorter than the tolerance ``tol`` of
      `Brent` moves at most ``tol`` from ``b``, less than half the interval while the solve runs;
    - an interpolation step to exactly the midpoint does not occur on the rows of Table 2.
    """
    # As at the label ``int`` of Brent's Algol procedure ``zero``, c starts as a, the bound on the other side of the
    # root from b.
    (c, fc), (b, fb) = history[0], history[1]
    n_bisection_switches = 0
    for x, fx in history[2:]:
        # As at the label ``ext`` of ``zero``, b becomes the bound with the smaller |f|.
        if abs(fc) < abs(fb):
            b, c = c, b
            fb, fc = fc, fb
        if x == b + 0.5 * (c - b):
            n_bisection_switches += 1
        previous_b, previous_fb = b, fb
        b, fb = x, fx
        if (fb > 0.0) == (fc > 0.0):
            # b crossed the root, so its previous value becomes c.
            c, fc = previous_b, previous_fb
    return n_bisection_switches
