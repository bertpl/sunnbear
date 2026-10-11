"""These tests assert that every variant of `Ridders` reproduces the first iteration of the example in its paper, and
every iterate that Section III of that paper prints."""

import math
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal

import pytest

from sunnbear.solvers import Ridders, RiddersVariant


@pytest.mark.parametrize("variant", RiddersVariant)
def test_the_first_iteration_reproduces_the_example_of_the_paper(variant):
    """On the paper's example, ``x^3 - x - 5`` on ``[-1, 3]``, the first iterate is 1.9128..., and the next interval
    is ``[1, 1.9128...]``, whose midpoint is the next point evaluated."""
    # --- act --------------------------
    result = Ridders(variant=variant).solve(
        lambda x: x**3 - x - 5.0, -1.0, 3.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    (x1, f1), (x3, _), (x1_next, _) = result.history[2:5]
    assert (x1, f1) == (1.0, -5.0)
    assert x3 == 1.0 + 2.0 * 1.0 / math.sqrt(1.0 - 19.0 / -5.0)  # f1 / f0 = 1 and f2 / f0 = -19 / 5
    assert 1.9128 < x3 < 1.9129  # The paper prints the iterate as 1.9128..., truncated.
    assert x1_next == 0.5 * (1.0 + x3)


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize(
    "f, a, b, printed_iterates",
    [
        pytest.param(
            lambda x: x * math.exp(x) - 10.0,
            -10.0,
            10.0,
            ["0.06...", "2.75...", "1.71...", "1.746...", "1.74552798...", "1.745528003"],
            id="x*exp(x)-10[-10,10]",
        ),
        pytest.param(
            lambda x: x * math.exp(x) - 10.0,
            -100.0,
            100.0,
            ["6e-21...", "7.74...", "2.38...", "1.709...", "1.7458...", "1.745527990...", "1.745528003"],
            id="x*exp(x)-10[-100,100]",
        ),
        pytest.param(
            lambda x: math.tan(x) ** math.tan(x) - 1.0e3,
            1.3,
            1.4,
            ["1.352...", "1.356...", "1.3547099...", "1.354710442"],
            id="tan^tan-1e3[1.3,1.4]",
        ),
        pytest.param(
            lambda x: math.tan(x) ** math.tan(x) - 1.0e3,
            0.0,
            1.5,
            ["0.75...", "1.12...", "1.31...", "1.40...", "1.357...", "1.35429...", "1.354710756", "1.354710442"],
            id="tan^tan-1e3[0,1.5]",
        ),
        pytest.param(
            lambda x: math.sin(math.radians(x)),
            10.0,
            280.0,
            ["254.50...", "177.09...", "179.97...", "179.99995...", "180"],
            id="sin(x_degrees)[10,280]",
        ),
    ],
)
def test_the_iterates_of_section_iii_of_the_paper_are_reproduced(variant, f, a, b, printed_iterates):
    """On each run in Section III of the paper, the new points ``x3`` that each iteration computes from its interval
    and that interval's midpoint match every iterate that the paper prints, to the printed digits.

    The paper truncates a printed iterate that ends in "...", and rounds a printed iterate that does not; the test
    truncates or rounds each computed iterate to match.

    The paper states no stopping rule, so the test compares only the iterates that the paper prints. The tight
    ``xtol`` and large ``max_fevals`` keep every variant running past the last printed iterate.

    All variants match the same printed iterates: they differ in their stopping rules, and the ``"scipy"`` variant
    also keeps each iterate at least ``xtol / 2`` inside the interval, which at this ``xtol`` changes no printed digit.
    """
    # --- act --------------------------
    result = Ridders(variant=variant).solve(f, a, b, xtol=1e-12, max_fevals=200, history_enabled=True)

    # --- assert -----------------------
    # After the 2 interval bounds, each iteration evaluates its midpoint and then its iterate x3.
    iterates = result.evaluated_x_values[3::2][: len(printed_iterates)]
    assert len(iterates) == len(printed_iterates)
    for x3, printed_iterate in zip(iterates, printed_iterates, strict=True):
        is_truncated = printed_iterate.endswith("...")
        printed_value = Decimal(printed_iterate.removesuffix("..."))
        rounding = ROUND_DOWN if is_truncated else ROUND_HALF_EVEN
        assert Decimal(x3).quantize(printed_value, rounding=rounding) == printed_value, printed_iterate
