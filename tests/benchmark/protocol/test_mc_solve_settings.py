"""`MCSolveSettings` maps each tuple's u log-uniformly onto the `xtol` range and its v linearly onto the c-range, and
gives every solve the evaluation budget of `max_fevals_for`."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.protocol import CRange, MCSolveSettings, compute_xtol_range, max_fevals_for
from sunnbear._core.problems.core import FormulaRegistry


def test_the_settings_map_u_log_uniformly_onto_the_xtol_range_and_v_linearly_onto_the_c_range():
    """u = 0.5 lands at the geometric mean of the bounds of the `xtol` range, and v places c linearly within the
    c-range."""
    # --- arrange ----------------------
    mc_tuples = MCTuples([0.5, 0.25], [0.5, 0.25])
    xtol_min, xtol_max = compute_xtol_range(a=-1.0, b=3.0, n_bisection_fevals=5)

    # --- act --------------------------
    settings = MCSolveSettings(
        a=-1.0, b=3.0, n_bisection_fevals=5, c_range=CRange(c_min=-2.0, c_max=2.0), mc_tuples=mc_tuples
    )

    # --- assert -----------------------
    assert settings.xtols == pytest.approx([np.sqrt(xtol_min * xtol_max), xtol_min * (xtol_max / xtol_min) ** 0.25])
    assert settings.cs == pytest.approx([0.0, -1.0])
    assert settings.max_fevals == max_fevals_for(n_bisection_fevals=5)


def test_the_settings_of_a_test_problem_take_its_interval_and_its_c_range():
    """`from_test_problem` takes the interval bounds and the c-range from the calibrated test problem."""
    # --- arrange ----------------------
    problem = FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(c_min=-1.0, c_max=0.5)
    mc_tuples = MCTuples([0.5, 0.25], [0.5, 0.25])

    # --- act --------------------------
    settings = MCSolveSettings.from_test_problem(problem, n_bisection_fevals=40, mc_tuples=mc_tuples)

    # --- assert -----------------------
    assert (settings.a, settings.b) == (problem.a, problem.b)
    assert settings.c_range == CRange(c_min=-1.0, c_max=0.5)
    assert settings.n_bisection_fevals == 40
    assert settings.mc_tuples is mc_tuples
